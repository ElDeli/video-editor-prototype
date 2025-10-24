from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from pathlib import Path
import os
import uuid

uploads_bp = Blueprint('uploads', __name__)

# Upload directories in Dropbox
DROPBOX_BASE = Path(os.path.expanduser('~/Dropbox/Apps/output Horoskop/video_editor_prototype/uploads'))
AUDIO_UPLOAD_DIR = DROPBOX_BASE / 'audio'
IMAGE_UPLOAD_DIR = DROPBOX_BASE / 'images'

# Allowed file extensions
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'm4a', 'aac', 'ogg'}
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}

# Max file sizes (in bytes)
MAX_AUDIO_SIZE = 50 * 1024 * 1024  # 50MB
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB

# Create upload directories if they don't exist
AUDIO_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
IMAGE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_unique_filename(original_filename):
    """Generate unique filename while preserving extension"""
    ext = original_filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    return unique_name

@uploads_bp.route('/uploads/audio', methods=['POST'])
def upload_audio():
    """Upload background music file"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Validate file extension
        if not allowed_file(file.filename, ALLOWED_AUDIO_EXTENSIONS):
            return jsonify({
                'error': f'Invalid file type. Allowed types: {", ".join(ALLOWED_AUDIO_EXTENSIONS)}'
            }), 400

        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > MAX_AUDIO_SIZE:
            return jsonify({
                'error': f'File too large. Maximum size: {MAX_AUDIO_SIZE // (1024 * 1024)}MB'
            }), 400

        # Generate unique filename
        unique_filename = get_unique_filename(file.filename)
        file_path = AUDIO_UPLOAD_DIR / unique_filename

        # Save file
        file.save(str(file_path))

        return jsonify({
            'success': True,
            'filename': unique_filename,
            'path': str(file_path),
            'original_name': file.filename,
            'size': file_size
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@uploads_bp.route('/uploads/image', methods=['POST'])
def upload_image():
    """Upload scene background image"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Validate file extension
        if not allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
            return jsonify({
                'error': f'Invalid file type. Allowed types: {", ".join(ALLOWED_IMAGE_EXTENSIONS)}'
            }), 400

        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > MAX_IMAGE_SIZE:
            return jsonify({
                'error': f'File too large. Maximum size: {MAX_IMAGE_SIZE // (1024 * 1024)}MB'
            }), 400

        # Generate unique filename
        unique_filename = get_unique_filename(file.filename)
        file_path = IMAGE_UPLOAD_DIR / unique_filename

        # Save file
        file.save(str(file_path))

        return jsonify({
            'success': True,
            'filename': unique_filename,
            'path': str(file_path),
            'original_name': file.filename,
            'size': file_size
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@uploads_bp.route('/uploads/audio/<filename>', methods=['GET'])
def serve_audio(filename):
    """Serve uploaded audio file"""
    try:
        return send_from_directory(AUDIO_UPLOAD_DIR, filename)
    except Exception as e:
        return jsonify({'error': 'File not found'}), 404

@uploads_bp.route('/uploads/image/<filename>', methods=['GET'])
def serve_image(filename):
    """Serve uploaded image file"""
    try:
        return send_from_directory(IMAGE_UPLOAD_DIR, filename)
    except Exception as e:
        return jsonify({'error': 'File not found'}), 404

@uploads_bp.route('/uploads/audio/<filename>', methods=['DELETE'])
def delete_audio(filename):
    """Delete uploaded audio file"""
    try:
        file_path = AUDIO_UPLOAD_DIR / filename
        if file_path.exists():
            file_path.unlink()
            return jsonify({'success': True, 'message': 'File deleted'})
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@uploads_bp.route('/uploads/image/<filename>', methods=['DELETE'])
def delete_image(filename):
    """Delete uploaded image file"""
    try:
        file_path = IMAGE_UPLOAD_DIR / filename
        if file_path.exists():
            file_path.unlink()
            return jsonify({'success': True, 'message': 'File deleted'})
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
