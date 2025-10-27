"""
Preview Generator Service
Creates low-res preview videos from scenes
"""
import os
import json
from pathlib import Path
from datetime import datetime
from services.simple_video_generator import SimpleVideoGenerator
from services.translation_service import TranslationService

class PreviewGenerator:
    def __init__(self):
        self.output_dir = Path("./previews")
        self.output_dir.mkdir(exist_ok=True)
        self.translation_service = TranslationService()

    def generate_preview(self, project_id, scenes, tts_voice='de-DE-KatjaNeural', background_music_path=None, background_music_volume=7, target_language='auto', video_speed=1.0, ai_image_model='flux-dev', resolution='preview'):
        """
        Generate preview video from scenes using actual video generation
        """
        if not scenes:
            raise ValueError("No scenes to preview")

        try:
            # Translate scene scripts if target_language is set (not 'auto')
            if target_language and target_language != 'auto':
                print(f"\n🌐 Translating {len(scenes)} scenes to {target_language}...")

                # Create a copy of scenes with translated scripts
                translated_scenes = []
                for scene in scenes:
                    scene_copy = dict(scene)  # Copy the scene dict
                    original_script = scene.get('script', '')

                    if original_script:
                        translated_script = self.translation_service.translate(original_script, target_language)
                        scene_copy['script'] = translated_script

                    translated_scenes.append(scene_copy)

                # Use translated scenes for video generation
                scenes = translated_scenes
                print("✓ Translation complete\n")

            # Initialize video generator with selected voice
            video_gen = SimpleVideoGenerator(tts_voice=tts_voice)

            # Generate actual video file (now returns timing data too)
            video_path, scene_timings = video_gen.generate_video(scenes, project_id, resolution=resolution, background_music_path=background_music_path, background_music_volume=background_music_volume, video_speed=video_speed, ai_image_model=ai_image_model)

            # Get video filename for URL
            video_filename = Path(video_path).name

            # Calculate total duration from actual timings
            total_duration = sum(t['duration'] for t in scene_timings)

            return {
                'preview_id': f"preview_{project_id}_{int(datetime.now().timestamp())}",
                'preview_path': video_path,
                'video_path': video_path,  # Add video_path for export endpoint
                'preview_url': f'/api/previews/{video_filename}',
                'total_duration': total_duration,
                'scene_count': len(scenes),
                'status': 'ready',
                'message': f'Preview video generated successfully! ({len(scenes)} scenes, {total_duration:.1f}s)',
                'scene_timings': scene_timings  # Include timing data for database updates
            }

        except Exception as e:
            # Fallback to JSON manifest if video generation fails
            print(f"Video generation failed: {e}")
            print("Falling back to JSON manifest...")

            preview_data = {
                'project_id': project_id,
                'created_at': datetime.now().isoformat(),
                'scenes': scenes,
                'total_duration': sum(s.get('duration', 5) for s in scenes),
                'format': 'preview',
                'resolution': '540p',
                'error': str(e)
            }

            preview_filename = f"preview_{project_id}_{int(datetime.now().timestamp())}.json"
            preview_path = self.output_dir / preview_filename

            with open(preview_path, 'w') as f:
                json.dump(preview_data, f, indent=2)

            return {
                'preview_id': preview_filename.replace('.json', ''),
                'preview_path': str(preview_path),
                'preview_url': None,
                'total_duration': preview_data['total_duration'],
                'scene_count': len(scenes),
                'status': 'error',
                'message': f'Video generation failed: {str(e)}'
            }
