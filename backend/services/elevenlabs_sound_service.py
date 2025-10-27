"""
ElevenLabs Sound Effects API Service
AI-powered sound effects generation
"""
import requests
import os
from pathlib import Path

class ElevenLabsSoundService:
    def __init__(self):
        self.api_key = os.getenv('ELEVENLABS_API_KEY', '')
        self.base_url = 'https://api.elevenlabs.io/v1'
        self.sound_dir = Path(os.path.expanduser('~/Dropbox/Apps/output Horoskop/output/video_editor_prototype/uploads/sound_effects'))
        self.sound_dir.mkdir(parents=True, exist_ok=True)

    def generate_sound_effect(self, text_prompt, duration_seconds=None):
        """
        Generate sound effect from text description using ElevenLabs AI

        Args:
            text_prompt: Text description of the sound effect (e.g., "explosion", "door closing")
            duration_seconds: Optional duration (0.5 to 22 seconds). If None, auto-generates

        Returns:
            Path to generated sound effect file
        """
        if not self.api_key:
            raise ValueError("ElevenLabs API key not configured")

        # Prepare API request
        url = f'{self.base_url}/sound-generation'

        headers = {
            'xi-api-key': self.api_key,
            'Content-Type': 'application/json'
        }

        payload = {
            'text': text_prompt,
            'model_id': 'eleven_text_to_sound_v2'  # Correct model for sound generation
        }

        # Add duration if specified
        if duration_seconds:
            if duration_seconds < 0.5 or duration_seconds > 22:
                raise ValueError("Duration must be between 0.5 and 22 seconds")
            payload['duration_seconds'] = duration_seconds

        try:
            print(f"🎵 Generating sound effect: '{text_prompt}'...")

            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()

            # Save audio file using hybrid storage
            filename = self._sanitize_filename(text_prompt) + '.mp3'
            rel_path = f'uploads/sound_effects/{filename}'
            file_path = storage.save_file(rel_path, response.content)

            print(f"✓ Sound effect saved: {file_path}")
            return str(file_path)

        except requests.exceptions.HTTPError as e:
            error_msg = f"ElevenLabs API error: {e}"
            if e.response.status_code == 401:
                error_msg = "Invalid ElevenLabs API key"
            elif e.response.status_code == 429:
                error_msg = "ElevenLabs API rate limit exceeded"
            elif e.response.status_code == 400:
                try:
                    error_detail = e.response.json()
                    error_msg = f"Invalid request: {error_detail.get('detail', 'Unknown error')}"
                except:
                    error_msg = "Invalid request to ElevenLabs API"
            raise Exception(error_msg)
        except Exception as e:
            raise Exception(f"Failed to generate sound effect: {e}")

    def _sanitize_filename(self, text):
        """Sanitize text for use as filename"""
        # Remove special characters, keep alphanumeric and spaces
        import re
        clean = re.sub(r'[^\w\s-]', '', text)
        # Replace spaces with underscores, limit length
        clean = clean.replace(' ', '_')[:50]
        return clean.lower()

    def test_connection(self):
        """Test if API key is valid"""
        try:
            # Try to generate a very short test sound
            test_sound = self.generate_sound_effect("click", duration_seconds=0.5)
            # Clean up test file
            if os.path.exists(test_sound):
                os.remove(test_sound)
            return True
        except:
            return False
