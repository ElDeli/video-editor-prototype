"""
OpenAI Translation Service
Translates text to target language for TTS generation
"""
import os
from openai import OpenAI

class TranslationService:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY', '')
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None

    def translate(self, text, target_language='auto'):
        """
        Translate text to target language using OpenAI GPT

        Args:
            text: Text to translate
            target_language: Target language code or 'auto' to keep original

        Returns:
            Translated text (or original if target_language is 'auto')
        """
        # If target is 'auto', return original text
        if target_language == 'auto' or not target_language:
            return text

        # If no API key, return original
        if not self.client:
            print("⚠️  No OpenAI API key configured - skipping translation")
            return text

        try:
            # Language mapping
            language_map = {
                'de': 'German',
                'en': 'English',
                'es': 'Spanish',
                'fr': 'French',
                'it': 'Italian',
                'pt': 'Portuguese',
                'pl': 'Polish',
                'nl': 'Dutch',
                'tr': 'Turkish',
                'ru': 'Russian',
                'ja': 'Japanese',
                'zh': 'Chinese',
                'ar': 'Arabic',
                'hi': 'Hindi'
            }

            target_lang_name = language_map.get(target_language, target_language)

            print(f"🌐 Translating text to {target_lang_name}...")

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Fast and cheap for translation
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional translator. Translate the following text to {target_lang_name}. ONLY return the translated text, nothing else. Preserve the tone and style of the original."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                temperature=0.3  # Low temperature for consistent translations
            )

            translated_text = response.choices[0].message.content.strip()
            print(f"✓ Translation complete")

            return translated_text

        except Exception as e:
            print(f"❌ Translation failed: {e}")
            print(f"   Returning original text")
            return text
