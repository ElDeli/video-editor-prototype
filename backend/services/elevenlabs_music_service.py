"""
ElevenLabs Music API Service
AI-powered music generation
"""
import requests
import os
from pathlib import Path
from services.dropbox_storage import storage

class ElevenLabsMusicService:
    def __init__(self):
        self.api_key = os.getenv('ELEVENLABS_API_KEY', '')
        self.base_url = 'https://api.elevenlabs.io/v1'
        self.music_dir = storage.get_save_dir('uploads/music')

    def generate_music(self, text_prompt, duration_seconds=None):
        """
        Generate music from text description using ElevenLabs AI

        Args:
            text_prompt: Text description (e.g., "upbeat electronic music", "calm piano")
            duration_seconds: Optional duration (0.5 to 22 seconds). If None, auto-generates

        Returns:
            Path to generated music file
        """
        if not self.api_key:
            raise ValueError("ElevenLabs API key not configured")

        # Use sound generation endpoint for music (same API, different prompts)
        url = f'{self.base_url}/sound-generation'

        headers = {
            'xi-api-key': self.api_key,
            'Content-Type': 'application/json'
        }

        payload = {
            'text': text_prompt,
            'model_id': 'eleven_text_to_sound_v2'
        }

        if duration_seconds:
            if duration_seconds < 0.5 or duration_seconds > 22:
                raise ValueError("Duration must be between 0.5 and 22 seconds")
            payload['duration_seconds'] = duration_seconds

        try:
            print(f"🎵 Generating music: '{text_prompt}'...")

            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()

            # Save audio file using hybrid storage
            filename = self._sanitize_filename(text_prompt) + '.mp3'
            rel_path = f'uploads/music/{filename}'

            # Save using hybrid storage (local or Dropbox API)
            file_path = storage.save_file(rel_path, response.content)

            print(f"✓ Music saved: {file_path}")
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
            raise Exception(f"Failed to generate music: {e}")

    def _sanitize_filename(self, text):
        """Sanitize text for use as filename"""
        import re
        clean = re.sub(r'[^\w\s-]', '', text)
        clean = clean.replace(' ', '_')[:50]
        return clean.lower()
