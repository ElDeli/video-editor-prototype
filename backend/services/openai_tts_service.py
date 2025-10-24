"""
OpenAI TTS Service
High-quality text-to-speech using OpenAI's TTS API
"""
import os
import requests
from pathlib import Path

class OpenAITTSService:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY', '')
        self.base_url = 'https://api.openai.com/v1'

        # Cache directory for voice samples
        self.samples_dir = Path('./openai_voice_samples')
        self.samples_dir.mkdir(exist_ok=True)

        # Available OpenAI TTS voices with characteristics
        self.voices = {
            'alloy': {
                'name': 'Alloy',
                'gender': 'Neutral',
                'description': 'Balanced and versatile',
                'tone': 'neutral',
                'pitch': 'medium',
                'style': 'versatile'
            },
            'echo': {
                'name': 'Echo',
                'gender': 'Male',
                'description': 'Clear and professional',
                'tone': 'clear',
                'pitch': 'medium-low',
                'style': 'professional'
            },
            'fable': {
                'name': 'Fable',
                'gender': 'Male',
                'description': 'Warm and expressive',
                'tone': 'warm',
                'pitch': 'medium',
                'style': 'expressive'
            },
            'onyx': {
                'name': 'Onyx',
                'gender': 'Male',
                'description': 'Deep and authoritative',
                'tone': 'deep',
                'pitch': 'low',
                'style': 'authoritative'
            },
            'nova': {
                'name': 'Nova',
                'gender': 'Female',
                'description': 'Bright and energetic',
                'tone': 'bright',
                'pitch': 'medium-high',
                'style': 'energetic'
            },
            'shimmer': {
                'name': 'Shimmer',
                'gender': 'Female',
                'description': 'Soft and gentle',
                'tone': 'soft',
                'pitch': 'high',
                'style': 'gentle'
            }
        }

    def get_available_voices(self):
        """
        Get list of available OpenAI TTS voices

        Returns:
            List of voice objects with characteristics
        """
        formatted_voices = []

        for voice_id, voice_data in self.voices.items():
            formatted_voices.append({
                'voice_id': voice_id,
                'value': f'openai:{voice_id}',  # Prefix to differentiate from other TTS
                'label': f"{voice_data['name']} ({voice_data['gender']})",
                'name': voice_data['name'],
                'gender': voice_data['gender'],
                'characteristics': {
                    'tone': voice_data['tone'],
                    'pitch': voice_data['pitch'],
                    'style': voice_data['style'],
                    'description': voice_data['description']
                }
            })

        return formatted_voices

    def generate_voice_sample(self, voice_id):
        """
        Generate a voice sample for preview

        Args:
            voice_id: OpenAI voice ID (alloy, echo, fable, onyx, nova, shimmer)

        Returns:
            Path to cached sample file
        """
        if voice_id not in self.voices:
            raise ValueError(f"Invalid voice ID: {voice_id}")

        # Check if sample exists in cache
        sample_filename = f"{voice_id}_sample.mp3"
        sample_path = self.samples_dir / sample_filename

        if sample_path.exists():
            print(f"✓ Serving cached OpenAI voice sample: {voice_id}")
            return str(sample_path)

        # Generate new sample
        print(f"🎤 Generating OpenAI voice sample: {voice_id}")

        if not self.api_key:
            raise ValueError("OpenAI API key not configured")

        url = f'{self.base_url}/audio/speech'
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        # Sample text for preview
        sample_text = "Hello! This is a voice sample. How does this voice sound?"

        payload = {
            'model': 'tts-1',
            'input': sample_text,
            'voice': voice_id
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            # Save audio file
            with open(sample_path, 'wb') as f:
                f.write(response.content)

            print(f"✓ OpenAI voice sample cached: {voice_id}")
            return str(sample_path)

        except requests.exceptions.HTTPError as e:
            error_msg = f"OpenAI API error: {e}"
            if e.response.status_code == 401:
                error_msg = "Invalid OpenAI API key"
            elif e.response.status_code == 429:
                error_msg = "OpenAI API rate limit exceeded"
            raise Exception(error_msg)
        except Exception as e:
            raise Exception(f"Failed to generate voice sample: {e}")

    def generate_tts(self, text, voice_id, output_path, model='tts-1'):
        """
        Generate TTS audio using OpenAI voice

        Args:
            text: Text to convert to speech
            voice_id: OpenAI voice ID (alloy, echo, fable, onyx, nova, shimmer)
            output_path: Where to save the audio file
            model: TTS model ('tts-1' for faster, 'tts-1-hd' for higher quality)

        Returns:
            Path to generated audio file
        """
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")

        if voice_id not in self.voices:
            raise ValueError(f"Invalid voice ID: {voice_id}")

        url = f'{self.base_url}/audio/speech'
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': model,
            'input': text,
            'voice': voice_id
        }

        try:
            print(f"🎤 Generating TTS with OpenAI voice {voice_id}...")

            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()

            # Save audio file
            with open(output_path, 'wb') as f:
                f.write(response.content)

            print(f"✓ TTS generated: {output_path}")
            return str(output_path)

        except requests.exceptions.HTTPError as e:
            error_msg = f"OpenAI API error: {e}"
            if e.response.status_code == 401:
                error_msg = "Invalid OpenAI API key"
            elif e.response.status_code == 429:
                error_msg = "OpenAI API rate limit exceeded"
            elif e.response.status_code == 400:
                try:
                    error_detail = e.response.json()
                    error_msg = f"Invalid request: {error_detail.get('error', {}).get('message', 'Unknown error')}"
                except:
                    error_msg = "Invalid request to OpenAI API"
            raise Exception(error_msg)
        except Exception as e:
            raise Exception(f"Failed to generate TTS: {e}")
