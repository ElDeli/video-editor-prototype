from flask import Blueprint, request, jsonify, send_file
from database.db_manager import DatabaseManager
from services.elevenlabs_sound_service import ElevenLabsSoundService
import os

sound_effects_bp = Blueprint('sound_effects', __name__)
db = DatabaseManager()
sound_service = ElevenLabsSoundService()

@sound_effects_bp.route('/sound-effects/generate', methods=['POST'])
def generate_sound_effect():
    """
    Generate a sound effect from text prompt using ElevenLabs AI

    Request body:
        {
            "text_prompt": "explosion",
            "duration": 2.5  // optional, 0.5-22 seconds
        }

    Returns:
        {
            "path": "/path/to/generated/sound.mp3",
            "text_prompt": "explosion"
        }
    """
    try:
        data = request.get_json()
        if not data or 'text_prompt' not in data:
            return jsonify({'error': 'text_prompt is required'}), 400

        text_prompt = data['text_prompt'].strip()
        if not text_prompt:
            return jsonify({'error': 'text_prompt cannot be empty'}), 400

        duration = data.get('duration')  # Optional

        # Generate sound effect using ElevenLabs
        sound_path = sound_service.generate_sound_effect(text_prompt, duration)

        return jsonify({
            'path': sound_path,
            'text_prompt': text_prompt
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sound_effects_bp.route('/scenes/<int:scene_id>/sound-effect', methods=['POST'])
def add_sound_effect_to_scene(scene_id):
    """
    Add sound effect to a scene

    Request body:
        {
            "sound_effect_path": "/path/to/sound.mp3"
        }

    Returns:
        Updated scene object
    """
    try:
        scene = db.get_scene(scene_id)
        if not scene:
            return jsonify({'error': 'Scene not found'}), 404

        data = request.get_json()
        if not data or 'sound_effect_path' not in data:
            return jsonify({'error': 'sound_effect_path is required'}), 400

        # Update scene with sound effect path
        updated_scene = db.update_scene(scene_id, {
            'sound_effect_path': data['sound_effect_path']
        })

        return jsonify(updated_scene)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sound_effects_bp.route('/scenes/<int:scene_id>/sound-effect', methods=['DELETE'])
def remove_sound_effect_from_scene(scene_id):
    """
    Remove sound effect from a scene

    Returns:
        Updated scene object
    """
    try:
        scene = db.get_scene(scene_id)
        if not scene:
            return jsonify({'error': 'Scene not found'}), 404

        # Remove sound effect path from scene
        updated_scene = db.update_scene(scene_id, {
            'sound_effect_path': None
        })

        return jsonify(updated_scene)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sound_effects_bp.route('/scenes/<int:scene_id>/sound-effect/audio', methods=['GET'])
def get_sound_effect_audio(scene_id):
    """
    Serve sound effect audio file for preview

    Returns:
        Audio file stream (MP3)
    """
    try:
        scene = db.get_scene(scene_id)
        if not scene or not scene.get('sound_effect_path'):
            return jsonify({'error': 'Sound effect not found'}), 404

        audio_path = scene['sound_effect_path']
        if not os.path.exists(audio_path):
            return jsonify({'error': 'Audio file not found'}), 404

        return send_file(audio_path, mimetype='audio/mpeg')

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sound_effects_bp.route('/scenes/<int:scene_id>/sound-effect/generate', methods=['POST'])
def generate_and_add_sound_effect(scene_id):
    """
    Generate sound effect from text and immediately add it to scene

    Request body:
        {
            "text_prompt": "explosion",
            "duration": 2.5  // optional
        }

    Returns:
        Updated scene object with sound_effect_path
    """
    try:
        scene = db.get_scene(scene_id)
        if not scene:
            return jsonify({'error': 'Scene not found'}), 404

        data = request.get_json()
        if not data or 'text_prompt' not in data:
            return jsonify({'error': 'text_prompt is required'}), 400

        text_prompt = data['text_prompt'].strip()
        duration = data.get('duration')

        # Generate sound effect
        sound_path = sound_service.generate_sound_effect(text_prompt, duration)

        # Add to scene
        updated_scene = db.update_scene(scene_id, {
            'sound_effect_path': sound_path
        })

        return jsonify(updated_scene)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
