"""
Music Generation API Endpoints
ElevenLabs AI-powered music generation
"""
from flask import Blueprint, request, jsonify
from services.elevenlabs_music_service import ElevenLabsMusicService

music_bp = Blueprint('music', __name__)
music_service = ElevenLabsMusicService()

@music_bp.route('/music/generate', methods=['POST'])
def generate_music():
    """
    Generate background music from text description

    Request JSON:
    {
        "text_prompt": "upbeat electronic music",
        "project_id": 1,  // optional - if provided, music duration matches video length
        "duration_seconds": 10  // optional, 0.5-22 seconds (overrides project_id)
    }

    Returns:
    {
        "success": true,
        "path": "/path/to/music.mp3",
        "filename": "upbeat_electronic_music.mp3",
        "duration": 10.5  // actual duration generated
    }
    """
    try:
        data = request.get_json()

        if not data or 'text_prompt' not in data:
            return jsonify({'error': 'text_prompt is required'}), 400

        text_prompt = data['text_prompt']
        duration_seconds = data.get('duration_seconds')  # Optional
        project_id = data.get('project_id')  # Optional

        # If no explicit duration provided, calculate from project scenes
        if duration_seconds is None and project_id:
            from database.db_manager import DatabaseManager
            db = DatabaseManager()

            # Get project scenes to calculate total duration
            project = db.get_project(project_id)
            if project:
                scenes = db.get_project_scenes(project_id)  # FIXED: correct method name
                if scenes:
                    # Calculate total video duration from scenes
                    total_duration = sum(scene.get('duration', 5) for scene in scenes)

                    # ElevenLabs max is 22 seconds, so cap it
                    # Music will loop automatically in video if shorter than total
                    duration_seconds = min(total_duration, 22)

                    print(f"🎵 Calculated music duration: {duration_seconds:.1f}s (video: {total_duration:.1f}s)")
                else:
                    # No scenes yet, use default 10 seconds
                    duration_seconds = 10
                    print(f"⚠️ No scenes found, using default duration: 10s")

        # Validate duration if provided
        if duration_seconds is not None:
            try:
                duration_seconds = float(duration_seconds)
                if duration_seconds < 0.5 or duration_seconds > 22:
                    return jsonify({'error': 'duration_seconds must be between 0.5 and 22'}), 400
            except (ValueError, TypeError):
                return jsonify({'error': 'duration_seconds must be a number'}), 400

        # Generate music
        music_path = music_service.generate_music(text_prompt, duration_seconds)

        # Extract filename from path
        import os
        filename = os.path.basename(music_path)

        return jsonify({
            'success': True,
            'path': music_path,
            'filename': filename,
            'duration': duration_seconds  # Return actual duration used
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to generate music: {str(e)}'}), 500

@music_bp.route('/music/test', methods=['GET'])
def test_music_api():
    """Test if ElevenLabs Music API is configured"""
    try:
        if not music_service.api_key:
            return jsonify({
                'configured': False,
                'error': 'ElevenLabs API key not configured'
            }), 200

        return jsonify({
            'configured': True,
            'message': 'ElevenLabs Music API ready'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
