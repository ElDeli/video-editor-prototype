"""
ElevenLabs Voice Service
Premium TTS voices with high quality
"""
import requests
import os
from pathlib import Path

class ElevenLabsVoiceService:
    def __init__(self):
        self.api_key = os.getenv('ELEVENLABS_API_KEY', '')
        self.base_url = 'https://api.elevenlabs.io/v1'

        # Cache directory for voice samples
        self.samples_dir = Path('./elevenlabs_voice_samples')
        self.samples_dir.mkdir(exist_ok=True)

    def get_available_voices(self):
        """
        Fetch available ElevenLabs voices

        Returns:
            List of voice objects with id, name, labels, preview_url
        """
        if not self.api_key:
            raise ValueError("ElevenLabs API key not configured")

        url = f'{self.base_url}/voices'
        headers = {
            'xi-api-key': self.api_key
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()
            voices = data.get('voices', [])

            # Format voices for frontend
            formatted_voices = []
            for voice in voices:
                formatted_voices.append({
                    'voice_id': voice.get('voice_id'),
                    'name': voice.get('name'),
                    'labels': voice.get('labels', {}),
                    'preview_url': voice.get('preview_url'),
                    'category': voice.get('category', 'general'),
                    'description': voice.get('description', ''),
                })

            return formatted_voices

        except requests.exceptions.HTTPError as e:
            error_msg = f"ElevenLabs API error: {e}"
            if e.response.status_code == 401:
                error_msg = "Invalid ElevenLabs API key"
            elif e.response.status_code == 429:
                error_msg = "ElevenLabs API rate limit exceeded"
            raise Exception(error_msg)
        except Exception as e:
            raise Exception(f"Failed to fetch ElevenLabs voices: {e}")

    def download_voice_sample(self, voice_id, voice_name, preview_url):
        """
        Download and cache voice preview sample

        Args:
            voice_id: ElevenLabs voice ID
            voice_name: Voice name (for filename)
            preview_url: URL to preview audio

        Returns:
            Path to cached sample file
        """
        # Sanitize filename
        safe_name = voice_name.replace(' ', '_').replace('/', '_')
        sample_filename = f"{voice_id}_{safe_name}.mp3"
        sample_path = self.samples_dir / sample_filename

        # Return cached file if exists
        if sample_path.exists():
            print(f"✓ Serving cached ElevenLabs voice sample: {voice_name}")
            return str(sample_path)

        # Download preview
        try:
            print(f"🎤 Downloading ElevenLabs voice sample: {voice_name}")

            response = requests.get(preview_url, timeout=30)
            response.raise_for_status()

            with open(sample_path, 'wb') as f:
                f.write(response.content)

            print(f"✓ ElevenLabs voice sample cached: {voice_name}")
            return str(sample_path)

        except Exception as e:
            raise Exception(f"Failed to download voice sample: {e}")

    def generate_tts(self, text, voice_id, output_path):
        """
        Generate TTS audio using ElevenLabs voice

        Args:
            text: Text to convert to speech
            voice_id: ElevenLabs voice ID
            output_path: Where to save the audio file

        Returns:
            Path to generated audio file
        """
        if not self.api_key:
            raise ValueError("ElevenLabs API key not configured")

        url = f'{self.base_url}/text-to-speech/{voice_id}'
        headers = {
            'xi-api-key': self.api_key,
            'Content-Type': 'application/json'
        }

        payload = {
            'text': text,
            'model_id': 'eleven_multilingual_v2',
            'voice_settings': {
                'stability': 0.5,
                'similarity_boost': 0.75
            }
        }

        try:
            print(f"🎤 Generating TTS with ElevenLabs voice {voice_id}...")

            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()

            # Save audio file
            with open(output_path, 'wb') as f:
                f.write(response.content)

            print(f"✓ TTS generated: {output_path}")
            return str(output_path)

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
            raise Exception(f"Failed to generate TTS: {e}")
