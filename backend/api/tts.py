from flask import Blueprint, jsonify, send_file
import asyncio
import edge_tts
import os
from pathlib import Path
import hashlib
from services.elevenlabs_voice_service import ElevenLabsVoiceService
from services.openai_tts_service import OpenAITTSService

tts_bp = Blueprint('tts', __name__)

# Initialize voice services
elevenlabs_voice_service = ElevenLabsVoiceService()
openai_tts_service = OpenAITTSService()

# Voice samples cache directory
VOICE_SAMPLES_DIR = Path('./voice_samples')
VOICE_SAMPLES_DIR.mkdir(exist_ok=True)

# Voice characteristics database
VOICE_CHARACTERISTICS = {
    # German voices - detailed characteristics
    'de-DE-KatjaNeural': {'tone': 'warm', 'pitch': 'medium', 'age': 'adult', 'style': 'friendly', 'description': 'Warm und freundlich'},
    'de-DE-ConradNeural': {'tone': 'deep', 'pitch': 'low', 'age': 'mature', 'style': 'professional', 'description': 'Tief und professionell'},
    'de-DE-AmalaNeural': {'tone': 'soft', 'pitch': 'medium-high', 'age': 'young', 'style': 'gentle', 'description': 'Sanft und jung'},
    'de-DE-BerndNeural': {'tone': 'strong', 'pitch': 'medium-low', 'age': 'mature', 'style': 'confident', 'description': 'Stark und selbstbewusst'},
    'de-DE-ChristophNeural': {'tone': 'neutral', 'pitch': 'medium', 'age': 'adult', 'style': 'clear', 'description': 'Klar und neutral'},
    'de-DE-ElkeNeural': {'tone': 'bright', 'pitch': 'medium-high', 'age': 'adult', 'style': 'cheerful', 'description': 'Hell und fröhlich'},
    'de-DE-GiselaNeural': {'tone': 'warm', 'pitch': 'medium', 'age': 'mature', 'style': 'caring', 'description': 'Warm und fürsorglich'},
    'de-DE-KasperNeural': {'tone': 'strong', 'pitch': 'low', 'age': 'mature', 'style': 'authoritative', 'description': 'Stark und autoritär'},
    'de-DE-KillianNeural': {'tone': 'energetic', 'pitch': 'medium', 'age': 'young-adult', 'style': 'dynamic', 'description': 'Energisch und dynamisch'},
    'de-DE-KlarissaNeural': {'tone': 'soft', 'pitch': 'medium-high', 'age': 'adult', 'style': 'elegant', 'description': 'Sanft und elegant'},
    'de-DE-LouisaNeural': {'tone': 'gentle', 'pitch': 'medium-high', 'age': 'young-adult', 'style': 'sweet', 'description': 'Sanft und süß'},
    'de-DE-MajaNeural': {'tone': 'bright', 'pitch': 'high', 'age': 'young', 'style': 'lively', 'description': 'Hell und lebhaft'},
    'de-DE-RalfNeural': {'tone': 'deep', 'pitch': 'low', 'age': 'mature', 'style': 'serious', 'description': 'Tief und seriös'},
    'de-DE-TanjaNeural': {'tone': 'warm', 'pitch': 'medium', 'age': 'adult', 'style': 'friendly', 'description': 'Warm und freundlich'},

    # English (US) - popular voices
    'en-US-JennyNeural': {'tone': 'warm', 'pitch': 'medium', 'age': 'adult', 'style': 'friendly', 'description': 'Warm and friendly'},
    'en-US-GuyNeural': {'tone': 'neutral', 'pitch': 'medium', 'age': 'adult', 'style': 'professional', 'description': 'Clear and professional'},
    'en-US-AriaNeural': {'tone': 'bright', 'pitch': 'medium-high', 'age': 'young-adult', 'style': 'energetic', 'description': 'Bright and energetic'},
    'en-US-DavisNeural': {'tone': 'deep', 'pitch': 'low', 'age': 'mature', 'style': 'authoritative', 'description': 'Deep and authoritative'},
    'en-US-JaneNeural': {'tone': 'soft', 'pitch': 'medium-high', 'age': 'adult', 'style': 'gentle', 'description': 'Soft and gentle'},
    'en-US-JasonNeural': {'tone': 'strong', 'pitch': 'medium-low', 'age': 'adult', 'style': 'confident', 'description': 'Strong and confident'},

    # English (UK) - popular voices
    'en-GB-SoniaNeural': {'tone': 'warm', 'pitch': 'medium', 'age': 'adult', 'style': 'friendly', 'description': 'Warm British accent'},
    'en-GB-RyanNeural': {'tone': 'neutral', 'pitch': 'medium', 'age': 'adult', 'style': 'clear', 'description': 'Clear British accent'},
    'en-GB-LibbyNeural': {'tone': 'bright', 'pitch': 'medium-high', 'age': 'young-adult', 'style': 'cheerful', 'description': 'Bright and cheerful'},
    'en-GB-ThomasNeural': {'tone': 'strong', 'pitch': 'medium-low', 'age': 'mature', 'style': 'professional', 'description': 'Strong and professional'},
}

# Default characteristics for voices not in database
DEFAULT_CHARACTERISTICS = {
    'tone': 'neutral',
    'pitch': 'medium',
    'age': 'adult',
    'style': 'clear',
    'description': 'Clear and neutral'
}

def get_voice_characteristics(voice_name):
    """Get characteristics for a voice, or return defaults"""
    return VOICE_CHARACTERISTICS.get(voice_name, DEFAULT_CHARACTERISTICS)

@tts_bp.route('/tts/voices', methods=['GET'])
def get_voices():
    """Get list of available Edge TTS voices"""
    try:
        # Get voices asynchronously
        voices = asyncio.run(_get_edge_voices())

        # Group voices by language
        voice_groups = {}

        # Priority languages
        priority_langs = {
            'de': '🇩🇪 Deutsch',
            'en-US': '🇺🇸 English (US)',
            'en-GB': '🇬🇧 English (UK)',
            'fr': '🇫🇷 Français',
            'es': '🇪🇸 Español',
            'it': '🇮🇹 Italiano',
            'pt': '🇵🇹 Português',
            'pl': '🇵🇱 Polski',
            'nl': '🇳🇱 Nederlands',
            'tr': '🇹🇷 Türkçe',
            'ru': '🇷🇺 Русский',
            'ja': '🇯🇵 日本語',
            'zh': '🇨🇳 中文',
            'ar': '🇸🇦 العربية',
            'hi': '🇮🇳 हिन्दी'
        }

        for voice in voices:
            locale = voice['locale']
            lang_code = locale.split('-')[0]

            # Only include priority languages
            lang_key = None
            if locale.startswith('en-US') or locale.startswith('en-GB'):
                lang_key = locale[:5]  # Keep en-US and en-GB separate
            elif lang_code in priority_langs:
                lang_key = lang_code

            if lang_key:
                if lang_key not in voice_groups:
                    voice_groups[lang_key] = []

                # Clean up the name (remove locale suffix)
                name = voice['short_name'].split('-')[-1].replace('Neural', '')

                # Get voice characteristics
                characteristics = get_voice_characteristics(voice['short_name'])

                voice_groups[lang_key].append({
                    'value': voice['short_name'],
                    'label': f"{name} ({voice['gender']})",
                    'locale': locale,
                    'gender': voice['gender'],
                    'characteristics': characteristics
                })

        # Format for dropdown with groups
        formatted_groups = []
        for lang_key in priority_langs.keys():
            if lang_key in voice_groups:
                formatted_groups.append({
                    'label': priority_langs[lang_key],
                    'options': sorted(voice_groups[lang_key], key=lambda x: x['label'])
                })

        return jsonify({'voice_groups': formatted_groups})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tts_bp.route('/tts/preview/<voice_name>', methods=['GET'])
def get_voice_preview(voice_name):
    """Generate and serve a preview sample for a voice (cached)"""
    try:
        # Create unique filename for this voice
        sample_filename = f"{voice_name}.mp3"
        sample_path = VOICE_SAMPLES_DIR / sample_filename

        # Check if sample already exists in cache
        if sample_path.exists():
            print(f"✓ Serving cached voice sample: {voice_name}")
            return send_file(sample_path, mimetype='audio/mpeg')

        # Generate new sample
        print(f"🎤 Generating voice sample for: {voice_name}")

        # Get sample text based on language
        locale = voice_name.split('-')[0:2]
        locale_code = '-'.join(locale)

        sample_texts = {
            'de': 'Hallo! Dies ist eine Sprachprobe. Wie klingt diese Stimme?',
            'en': 'Hello! This is a voice sample. How does this voice sound?',
            'fr': 'Bonjour! Ceci est un échantillon vocal. Comment cette voix sonne-t-elle?',
            'es': '¡Hola! Esta es una muestra de voz. ¿Cómo suena esta voz?',
            'it': 'Ciao! Questo è un campione vocale. Come suona questa voce?',
            'pt': 'Olá! Esta é uma amostra de voz. Como é que esta voz soa?',
            'pl': 'Cześć! To jest próbka głosu. Jak brzmi ten głos?',
            'nl': 'Hallo! Dit is een spraakvoorbeeld. Hoe klinkt deze stem?',
            'tr': 'Merhaba! Bu bir ses örneğidir. Bu ses nasıl geliyor?',
            'ru': 'Привет! Это образец голоса. Как звучит этот голос?',
            'ja': 'こんにちは！これは音声サンプルです。この声はどう聞こえますか？',
            'zh': '你好！这是一个语音样本。这个声音听起来怎么样？',
            'ar': 'مرحبا! هذا نموذج صوتي. كيف يبدو هذا الصوت؟',
            'hi': 'नमस्ते! यह एक आवाज नमूना है। यह आवाज कैसी लगती है?'
        }

        lang_code = locale_code.split('-')[0]
        sample_text = sample_texts.get(lang_code, sample_texts['en'])

        # Generate audio using Edge TTS
        asyncio.run(_generate_voice_sample(voice_name, sample_text, sample_path))

        print(f"✓ Voice sample generated and cached: {voice_name}")
        return send_file(sample_path, mimetype='audio/mpeg')

    except Exception as e:
        print(f"❌ Failed to generate voice sample: {e}")
        return jsonify({'error': str(e)}), 500

async def _generate_voice_sample(voice_name, text, output_path):
    """Generate voice sample using Edge TTS"""
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save(str(output_path))

async def _get_edge_voices():
    """Async function to fetch Edge TTS voices"""
    voices = await edge_tts.list_voices()
    return [
        {
            'short_name': v['ShortName'],
            'locale': v['Locale'],
            'gender': v['Gender']
        }
        for v in voices
    ]

# ============ ELEVENLABS PREMIUM VOICES ============

@tts_bp.route('/tts/elevenlabs/voices', methods=['GET'])
def get_elevenlabs_voices():
    """Get list of available ElevenLabs premium voices"""
    try:
        voices = elevenlabs_voice_service.get_available_voices()

        # Format voices with characteristics for frontend
        formatted_voices = []
        for voice in voices:
            # Extract characteristics from labels
            labels = voice.get('labels', {})
            accent = labels.get('accent', 'neutral')
            age = labels.get('age', 'adult')
            gender = labels.get('gender', 'neutral')
            use_case = labels.get('use case', 'general')

            formatted_voices.append({
                'value': f"elevenlabs:{voice['voice_id']}",  # Prefix to differentiate from Edge TTS
                'label': f"{voice['name']} ({gender})",
                'voice_id': voice['voice_id'],
                'characteristics': {
                    'tone': accent,
                    'pitch': age,
                    'style': use_case,
                    'description': voice.get('description', f"{accent} {gender} voice")
                }
            })

        return jsonify({
            'voices': formatted_voices
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tts_bp.route('/tts/elevenlabs/preview/<voice_id>', methods=['GET'])
def get_elevenlabs_voice_preview(voice_id):
    """Get cached preview for ElevenLabs voice"""
    try:
        # First, get voice info to get preview URL
        voices = elevenlabs_voice_service.get_available_voices()
        voice = next((v for v in voices if v['voice_id'] == voice_id), None)

        if not voice:
            return jsonify({'error': 'Voice not found'}), 404

        # Download and cache preview
        sample_path = elevenlabs_voice_service.download_voice_sample(
            voice_id,
            voice['name'],
            voice['preview_url']
        )

        return send_file(sample_path, mimetype='audio/mpeg')

    except Exception as e:
        print(f"❌ Failed to serve ElevenLabs voice preview: {e}")
        return jsonify({'error': str(e)}), 500

# ============ OPENAI TTS VOICES ============

@tts_bp.route('/tts/openai/voices', methods=['GET'])
def get_openai_voices():
    """Get list of available OpenAI TTS voices"""
    try:
        voices = openai_tts_service.get_available_voices()

        return jsonify({
            'voices': voices
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tts_bp.route('/tts/openai/preview/<voice_id>', methods=['GET'])
def get_openai_voice_preview(voice_id):
    """Generate and serve preview sample for OpenAI voice"""
    try:
        sample_path = openai_tts_service.generate_voice_sample(voice_id)
        return send_file(sample_path, mimetype='audio/mpeg')

    except Exception as e:
        print(f"❌ Failed to generate OpenAI voice preview: {e}")
        return jsonify({'error': str(e)}), 500
