from flask import Blueprint, request, jsonify, send_file
from database.db_manager import DatabaseManager
from services.preview_generator import PreviewGenerator
from services.keyword_extractor import KeywordExtractor
from services.replicate_image_service import ReplicateImageService
import os
import sys

projects_bp = Blueprint('projects', __name__)
db = DatabaseManager()
preview_gen = PreviewGenerator()
keyword_extractor = KeywordExtractor()

# Initialize Replicate service (REQUIRED)
image_service = ReplicateImageService()

@projects_bp.route('/projects', methods=['GET'])
def list_projects():
    """List all projects"""
    try:
        projects = db.list_projects()
        return jsonify(projects)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/projects', methods=['POST'])
def create_project():
    """Create a new project"""
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'error': 'Project name is required'}), 400

        project = db.create_project(data['name'])
        return jsonify(project), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """Get project with all scenes"""
    try:
        project = db.get_project(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404

        scenes = db.get_project_scenes(project_id)
        return jsonify({
            'project': project,
            'scenes': scenes
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/projects/<int:project_id>', methods=['PATCH', 'PUT'])
def update_project(project_id):
    """Update project settings"""
    try:
        project = db.get_project(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Build update dict
        updates = {}
        if 'tts_voice' in data:
            updates['tts_voice'] = data['tts_voice']
        if 'background_music_path' in data:
            updates['background_music_path'] = data['background_music_path']
        if 'background_music_volume' in data:
            updates['background_music_volume'] = data['background_music_volume']
        if 'video_speed' in data:
            updates['video_speed'] = data['video_speed']
        if 'target_language' in data:
            updates['target_language'] = data['target_language']
        if 'ai_image_model' in data:
            updates['ai_image_model'] = data['ai_image_model']

        # Apply updates
        if updates:
            db.update_project(project_id, updates)

        updated_project = db.get_project(project_id)
        return jsonify(updated_project)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/projects/<int:project_id>/scenes', methods=['POST'])
def add_scene(project_id):
    """Add a scene to project"""
    try:
        project = db.get_project(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404

        data = request.get_json()
        if not data or 'script' not in data:
            return jsonify({'error': 'Scene script is required'}), 400

        scene = db.add_scene(project_id, data)
        return jsonify(scene), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/projects/<int:project_id>/scenes/reorder', methods=['POST'])
def reorder_scenes(project_id):
    """Reorder scenes in project"""
    try:
        project = db.get_project(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404

        data = request.get_json()
        if not data or 'scene_ids' not in data:
            return jsonify({'error': 'scene_ids array is required'}), 400

        db.reorder_scenes(project_id, data['scene_ids'])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/projects/<int:project_id>/scenes/bulk', methods=['POST'])
def bulk_add_scenes(project_id):
    """Auto-create scenes from full script with visual keyword extraction"""
    try:
        project = db.get_project(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404

        data = request.get_json()
        if not data or 'full_script' not in data:
            return jsonify({'error': 'full_script is required'}), 400

        full_script = data['full_script'].strip()
        if not full_script:
            return jsonify({'error': 'Script cannot be empty'}), 400

        # Get target language from project (default to 'auto' - no translation)
        target_language = project.get('target_language', 'auto')

        # Translate full script if target_language is set (not 'auto')
        if target_language and target_language != 'auto':
            from services.translation_service import TranslationService
            translation_service = TranslationService()
            print(f"\n🌐 Translating script to {target_language}...")
            full_script = translation_service.translate(full_script, target_language)
            print("✓ Translation complete\n")

        # Use keyword extractor for visual storytelling
        visual_scenes = keyword_extractor.extract_visual_scenes(full_script)

        # Convert to database format and add
        created_scenes = []
        for scene_info in visual_scenes:
            scene_data = {
                'script': scene_info['script'],
                'duration': estimate_duration(scene_info['script']),
                'background_type': 'keyword' if scene_info['scene_type'] == 'keyword' else 'solid',
                'background_value': scene_info.get('visual_search') or '#000000'
            }
            scene = db.add_scene(project_id, scene_data)
            created_scenes.append(scene)

        return jsonify(created_scenes), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def parse_script_to_scenes(full_script):
    """
    Parse full script into individual scenes

    Strategy: Create 1 scene per sentence for maximum granularity
    Perfect for viral short-form content (TikTok/Reels style)
    """
    import re

    # Split by sentence endings (., !, ?, etc.)
    # Enhanced regex to handle common cases
    sentence_pattern = r'(?<=[.!?;:])\s+(?=[A-ZÄÖÜ"])|(?<=[.!?])\s*\n+\s*'
    sentences = re.split(sentence_pattern, full_script)

    # Clean up sentences
    sentences = [s.strip() for s in sentences if s.strip()]

    # If no sentences found, split by any punctuation
    if len(sentences) <= 1:
        sentences = re.split(r'[.!?;–—]+', full_script)
        sentences = [s.strip() for s in sentences if s.strip() and len(s) > 10]

    # Create one scene per sentence
    scenes = []
    for idx, sentence in enumerate(sentences):
        # Skip very short fragments (< 5 words)
        word_count = len(sentence.split())
        if word_count < 3:
            # Try to merge with previous scene if exists
            if scenes:
                scenes[-1]['script'] += ' ' + sentence
                scenes[-1]['duration'] = estimate_duration(scenes[-1]['script'])
            continue

        scenes.append({
            'script': sentence,
            'duration': estimate_duration(sentence),
            'background_type': 'solid',
            'background_value': '#000000'
        })

    # Fallback: if still only 1-2 scenes, force split by comma or word count
    if len(scenes) <= 2 and len(full_script.split()) > 20:
        scenes = []
        # Split by commas and sentence endings
        parts = re.split(r'[.!?;:,–—]+', full_script)
        parts = [p.strip() for p in parts if p.strip() and len(p.split()) >= 3]

        for part in parts:
            scenes.append({
                'script': part,
                'duration': estimate_duration(part),
                'background_type': 'solid',
                'background_value': '#000000'
            })

    # Ultimate fallback: return whole script as one scene
    return scenes if scenes else [{
        'script': full_script,
        'duration': estimate_duration(full_script),
        'background_type': 'solid',
        'background_value': '#000000'
    }]

def estimate_duration(text):
    """Estimate scene duration based on text length (assuming ~150 words/minute reading speed)"""
    words = len(text.split())
    duration = max(3, min(10, words / 2.5))  # 2.5 words per second, min 3s, max 10s
    return round(duration, 1)

@projects_bp.route('/projects/<int:project_id>/preview', methods=['POST'])
def generate_preview(project_id):
    """Generate low-res preview of project"""
    try:
        project = db.get_project(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404

        # Get all scenes - ALWAYS fresh from database to ensure sound effects are included
        scenes = db.get_project_scenes(project_id)
        if not scenes:
            return jsonify({'error': 'No scenes to preview'}), 400

        # DEBUG: Log sound effect info
        import sys
        for scene in scenes:
            if scene.get('sound_effect_path'):
                print(f"✓ Scene {scene['id']} HAS sound effect: {scene.get('sound_effect_path')} (Volume: {scene.get('sound_effect_volume', 50)}%)", file=sys.stderr, flush=True)
            else:
                print(f"  Scene {scene['id']} has NO sound effect", file=sys.stderr, flush=True)

        # Get TTS voice from project (default to German voice)
        tts_voice = project.get('tts_voice', 'de-DE-KatjaNeural')

        # Get background music path from project (optional)
        background_music_path = project.get('background_music_path')

        # Get background music volume from project (default to 7%)
        background_music_volume = project.get('background_music_volume', 7)

        # Get target language from project (default to 'auto' - no translation)
        target_language = project.get('target_language', 'auto')

        # Get video speed from project (default to 1.0 - normal speed)
        video_speed = project.get('video_speed', 1.0)

        # Get AI image model from project (default to flux-schnell - fast & cheap)
        ai_image_model = project.get('ai_image_model', 'flux-schnell')

        # Generate preview
        result = preview_gen.generate_preview(project_id, scenes, tts_voice=tts_voice, background_music_path=background_music_path, background_music_volume=background_music_volume, target_language=target_language, video_speed=video_speed, ai_image_model=ai_image_model)

        # Update scene durations in database with actual timings from video generation
        if 'scene_timings' in result:
            print(f"\n🔄 Syncing actual durations to database...", file=sys.stderr, flush=True)
            for timing in result['scene_timings']:
                scene_id = timing['id']
                actual_duration = round(timing['duration'], 2)  # Use 2 decimals for precision
                db_duration = timing['db_duration']

                if scene_id and actual_duration != db_duration:
                    print(f"   Scene {scene_id}: {db_duration}s → {actual_duration}s", file=sys.stderr, flush=True)
                    db.update_scene(scene_id, {'duration': actual_duration})
            print(f"✓ Database sync complete\n", file=sys.stderr, flush=True)

        # CRITICAL: Return updated scenes with actual durations so frontend can sync
        updated_scenes = db.get_project_scenes(project_id)
        result['updated_scenes'] = updated_scenes
        print(f"✓ Returning {len(updated_scenes)} updated scenes to frontend\n", file=sys.stderr, flush=True)

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/projects/<int:project_id>/export', methods=['POST'])
def export_video(project_id):
    """Export final video in 1080p"""
    try:
        project = db.get_project(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404

        # Get all scenes
        scenes = db.get_project_scenes(project_id)
        if not scenes:
            return jsonify({'error': 'No scenes to export'}), 400

        data = request.get_json() or {}
        resolution = data.get('resolution', '1080p')

        # Get project settings
        tts_voice = project.get('tts_voice', 'de-DE-KatjaNeural')
        background_music_path = project.get('background_music_path')
        background_music_volume = project.get('background_music_volume', 7)
        target_language = project.get('target_language', 'auto')
        video_speed = project.get('video_speed', 1.0)
        ai_image_model = project.get('ai_image_model', 'flux-schnell')

        # Generate export video (full resolution)
        result = preview_gen.generate_preview(
            project_id,
            scenes,
            tts_voice=tts_voice,
            background_music_path=background_music_path,
            background_music_volume=background_music_volume,
            target_language=target_language,
            video_speed=video_speed,
            ai_image_model=ai_image_model,
            resolution=resolution
        )

        return jsonify({
            'success': True,
            'video_path': result.get('video_path'),
            'message': f'Export complete! Video saved to {result.get("video_path")}',
            'scene_count': result.get('scene_count'),
            'total_duration': result.get('total_duration')
        })
    except Exception as e:
        import traceback
        print(f"Export error: {traceback.format_exc()}", file=sys.stderr)
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/projects/<int:project_id>/download', methods=['GET'])
def download_video(project_id):
    """Download exported video file"""
    try:
        project = db.get_project(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404

        # Get resolution from query parameter (default 1080p)
        resolution = request.args.get('resolution', '1080p')

        # Build video path (check Dropbox location first, then local)
        dropbox_path = os.path.expanduser("~/Dropbox/Apps/output Horoskop/video_editor_prototype/previews")
        video_filename = f"video_{project_id}_{resolution}.mp4"

        # Try Dropbox location first (unified path)
        video_path = os.path.join(dropbox_path, video_filename)

        # Fallback to local backend/previews if not found in Dropbox
        if not os.path.exists(video_path):
            local_preview_dir = os.path.join(os.path.dirname(__file__), '..', 'previews')
            video_path = os.path.join(local_preview_dir, video_filename)

        if not os.path.exists(video_path):
            print(f"Video not found at: {video_path}", file=sys.stderr)
            return jsonify({'error': f'Video not found. Please export first.'}), 404

        print(f"✓ Serving video from: {video_path}", file=sys.stderr)

        # Send file with download prompt
        return send_file(
            video_path,
            mimetype='video/mp4',
            as_attachment=True,
            download_name=f"{project['name']}_{resolution}.mp4"
        )

    except Exception as e:
        print(f"Error downloading video: {e}", file=sys.stderr)
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/projects/<int:project_id>/upload-to-queue', methods=['POST'])
def upload_to_queue(project_id):
    """Copy video to output folder queue"""
    try:
        import shutil

        project = db.get_project(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404

        data = request.get_json() or {}
        folder_id = data.get('folder_id')
        resolution = data.get('resolution', '1080p')

        # Get output folder
        if folder_id:
            output_folder = db.get_output_folder(folder_id)
        else:
            output_folder = db.get_default_output_folder()

        if not output_folder:
            return jsonify({'error': 'No output folder specified or default folder not set'}), 400

        # Find source video file
        dropbox_path = os.path.expanduser("~/Dropbox/Apps/output Horoskop/video_editor_prototype/previews")
        video_filename = f"video_{project_id}_{resolution}.mp4"
        source_path = os.path.join(dropbox_path, video_filename)

        # Fallback to local if not found
        if not os.path.exists(source_path):
            local_preview_dir = os.path.join(os.path.dirname(__file__), '..', 'previews')
            source_path = os.path.join(local_preview_dir, video_filename)

        if not os.path.exists(source_path):
            print(f"Video not found at: {source_path}", file=sys.stderr)
            return jsonify({'error': 'Video not found. Please export first.'}), 404

        # Create destination path
        destination_folder = output_folder['path']
        os.makedirs(destination_folder, exist_ok=True)

        # Use project name for destination filename
        safe_name = "".join(c for c in project['name'] if c.isalnum() or c in (' ', '-', '_')).strip()
        destination_filename = f"{safe_name}_{resolution}.mp4"
        destination_path = os.path.join(destination_folder, destination_filename)

        # Copy video to output folder
        print(f"✓ Copying video from: {source_path}", file=sys.stderr)
        print(f"✓ To: {destination_path}", file=sys.stderr)
        shutil.copy2(source_path, destination_path)

        return jsonify({
            'success': True,
            'message': f'Video uploaded to {output_folder["name"]}',
            'destination_path': destination_path,
            'folder_name': output_folder['name']
        })

    except Exception as e:
        import traceback
        print(f"Upload to queue error: {traceback.format_exc()}", file=sys.stderr)
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/thumbnails/<path:keyword>', methods=['GET'])
def get_thumbnail(keyword):
    """Generate and serve thumbnail for keyword"""
    try:
        if not image_service:
            return jsonify({'error': 'Image service not available'}), 503

        # Use full-size image for now (already cached, so it's fast)
        # Later we can optimize to generate smaller thumbnails
        image_path = image_service.generate_image(keyword, width=608, height=1080)

        if not image_path or not os.path.exists(image_path):
            return jsonify({'error': f'Failed to generate thumbnail for: {keyword}'}), 500

        return send_file(image_path, mimetype='image/jpeg')

    except Exception as e:
        print(f"Error serving thumbnail: {e}")
        return jsonify({'error': str(e)}), 500
