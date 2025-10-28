from flask import Blueprint, request, jsonify
from database.db_manager import DatabaseManager
from services.replicate_image_service import ReplicateImageService
import random
import sys
import traceback

scenes_bp = Blueprint('scenes', __name__)
db = DatabaseManager()

# Initialize Replicate service
try:
    image_service = ReplicateImageService()
except:
    image_service = None

@scenes_bp.route('/scenes/<int:scene_id>', methods=['GET'])
def get_scene(scene_id):
    """Get scene by ID"""
    try:
        scene = db.get_scene(scene_id)
        if not scene:
            return jsonify({'error': 'Scene not found'}), 404
        return jsonify(scene)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@scenes_bp.route('/scenes/<int:scene_id>', methods=['PUT'])
def update_scene(scene_id):
    """Update scene"""
    try:
        scene = db.get_scene(scene_id)
        if not scene:
            return jsonify({'error': 'Scene not found'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # DEBUG: Log effect values if any are being updated
        effect_keys = ['effect_vignette', 'effect_color_temp', 'effect_saturation']
        effect_updates = {k: v for k, v in data.items() if k in effect_keys}
        if effect_updates:
            print(f"🔍 DEBUG: Scene {scene_id} effect updates: {effect_updates}", file=sys.stderr, flush=True)
            print(f"   Types: {', '.join([f'{k}={type(v).__name__}' for k, v in effect_updates.items()])}", file=sys.stderr, flush=True)

        updated_scene = db.update_scene(scene_id, data)

        # DEBUG: Log result effect values
        if effect_updates:
            result_effects = {k: updated_scene.get(k) for k in effect_keys if k in updated_scene}
            print(f"   Result: {result_effects}", file=sys.stderr, flush=True)

        return jsonify(updated_scene)
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"✗ Error updating scene {scene_id}: {e}", file=sys.stderr, flush=True)
        print(error_details, file=sys.stderr, flush=True)
        return jsonify({'error': str(e)}), 500

@scenes_bp.route('/scenes/<int:scene_id>', methods=['DELETE'])
def delete_scene(scene_id):
    """Delete scene"""
    try:
        scene = db.get_scene(scene_id)
        if not scene:
            return jsonify({'error': 'Scene not found'}), 404

        success = db.delete_scene(scene_id)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to delete scene'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@scenes_bp.route('/scenes/<int:scene_id>/regenerate-image', methods=['POST'])
def regenerate_scene_image(scene_id):
    """Regenerate image for a specific scene"""
    try:
        if not image_service:
            return jsonify({'error': 'Image service not available'}), 503

        scene = db.get_scene(scene_id)
        if not scene:
            return jsonify({'error': 'Scene not found'}), 404

        # Get project to determine AI model
        project = db.get_project(scene.get('project_id'))
        if not project:
            return jsonify({'error': 'Project not found'}), 404

        # Get AI model from project (default to flux-dev - balanced quality & cost)
        ai_image_model = project.get('ai_image_model', 'flux-dev')

        # Add random variation to keyword to force different image generation
        # This ensures we get a NEW image even for the same concept
        original_keyword = scene.get('background_value', 'cosmic')

        # Add variation suffix (variation 1, 2, 3, etc.)
        variation_num = random.randint(1, 100)
        new_keyword = f"{original_keyword} variation {variation_num}"

        # Force regeneration by bypassing cache
        print(f"🔄 Regenerating image for scene {scene_id}: {new_keyword} (model: {ai_image_model})")

        # Generate new image (will create new cache entry due to variation suffix)
        image_path = image_service.generate_image(new_keyword, width=608, height=1080, model=ai_image_model)

        if not image_path:
            return jsonify({'error': 'Failed to generate new image'}), 500

        # Update scene with new keyword
        db.update_scene(scene_id, {'background_value': new_keyword})

        print(f"✓ Scene {scene_id} image regenerated successfully")

        return jsonify({
            'success': True,
            'new_keyword': new_keyword,
            'message': 'Image regenerated successfully'
        })

    except Exception as e:
        error_details = traceback.format_exc()
        print(f"✗ Error regenerating image: {e}", file=sys.stderr, flush=True)
        print(error_details, file=sys.stderr, flush=True)
        return jsonify({'error': str(e)}), 500
