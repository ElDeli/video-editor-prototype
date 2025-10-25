from flask import Blueprint, request, jsonify
from database.db_manager import DatabaseManager
import sys
import os

settings_bp = Blueprint('settings', __name__)
db = DatabaseManager()

@settings_bp.route('/settings/output-folders', methods=['GET'])
def get_output_folders():
    """Get all output folders"""
    try:
        folders = db.get_output_folders()
        return jsonify(folders)
    except Exception as e:
        print(f"Error getting output folders: {e}", file=sys.stderr)
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/settings/output-folders', methods=['POST'])
def add_output_folder():
    """Add new output folder"""
    try:
        data = request.get_json()
        if not data or 'name' not in data or 'path' not in data:
            return jsonify({'error': 'Name and path are required'}), 400

        folder = db.add_output_folder(data['name'], data['path'])
        return jsonify(folder), 201
    except Exception as e:
        print(f"Error adding output folder: {e}", file=sys.stderr)
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/settings/output-folders/<int:folder_id>', methods=['DELETE'])
def delete_output_folder(folder_id):
    """Delete output folder"""
    try:
        db.delete_output_folder(folder_id)
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error deleting output folder: {e}", file=sys.stderr)
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/settings/output-folders/<int:folder_id>/set-default', methods=['POST'])
def set_default_output_folder(folder_id):
    """Set default output folder"""
    try:
        db.set_default_output_folder(folder_id)
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error setting default output folder: {e}", file=sys.stderr)
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/settings/output-folders/default', methods=['GET'])
def get_default_output_folder():
    """Get default output folder"""
    try:
        folder = db.get_default_output_folder()
        if not folder:
            return jsonify({'error': 'No default output folder set'}), 404
        return jsonify(folder)
    except Exception as e:
        print(f"Error getting default output folder: {e}", file=sys.stderr)
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/settings/browse-folders', methods=['GET'])
def browse_folders():
    """Browse filesystem folders"""
    try:
        path = request.args.get('path', os.path.expanduser('~'))
        path = os.path.expanduser(path)

        # Security: Ensure path is absolute and exists
        if not os.path.isabs(path):
            path = os.path.abspath(path)

        if not os.path.exists(path):
            return jsonify({'error': 'Path does not exist'}), 404

        if not os.path.isdir(path):
            # If it's a file, get its parent directory
            path = os.path.dirname(path)

        # Get parent directory
        parent = os.path.dirname(path) if path != '/' else None

        # List directories
        try:
            entries = []
            for item in sorted(os.listdir(path)):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    entries.append({
                        'name': item,
                        'path': item_path,
                        'isDir': True
                    })
        except PermissionError:
            return jsonify({'error': 'Permission denied'}), 403

        return jsonify({
            'currentPath': path,
            'parentPath': parent,
            'folders': entries
        })
    except Exception as e:
        print(f"Error browsing folders: {e}", file=sys.stderr)
        return jsonify({'error': str(e)}), 500
