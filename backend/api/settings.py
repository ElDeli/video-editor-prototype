from flask import Blueprint, request, jsonify
from database.db_manager import DatabaseManager
import sys
import os

settings_bp = Blueprint('settings', __name__)
db = DatabaseManager()

# Dropbox Output Base Path (works on both Railway and Local)
DROPBOX_OUTPUT_BASE = os.path.expanduser("~/Dropbox/Apps/output Horoskop/output")

# Predefined Output Folders for Dropbox
PREDEFINED_FOLDERS = [
    {
        'name': 'Instagram Reels',
        'path': os.path.join(DROPBOX_OUTPUT_BASE, 'viral_autonomous'),
        'description': 'Videos für Instagram Reels (9:16)'
    },
    {
        'name': 'YouTube Horoskop',
        'path': os.path.join(DROPBOX_OUTPUT_BASE, 'horoskop_content'),
        'description': 'Videos für YouTube Horoskop (9:16)'
    },
    {
        'name': 'TikTok',
        'path': os.path.join(DROPBOX_OUTPUT_BASE, 'tiktok'),
        'description': 'Videos für TikTok (9:16)'
    }
]

# Detect if running on Railway
IS_RAILWAY = os.getenv('RAILWAY_ENVIRONMENT') is not None or os.getenv('RAILWAY_SERVICE_NAME') is not None

def ensure_predefined_folders():
    """Ensure predefined Dropbox folders exist in database"""
    try:
        existing_folders = db.get_output_folders()
        existing_paths = {f['path'] for f in existing_folders}

        # Add predefined folders if they don't exist
        for folder in PREDEFINED_FOLDERS:
            if folder['path'] not in existing_paths:
                print(f"✓ Adding predefined folder: {folder['name']} -> {folder['path']}", file=sys.stderr)

                # Create physical directory if it doesn't exist
                os.makedirs(folder['path'], exist_ok=True)

                # Add to database
                db.add_output_folder(folder['name'], folder['path'])

        # Set first folder as default if no default exists
        default = db.get_default_output_folder()
        if not default:
            all_folders = db.get_output_folders()
            if all_folders:
                db.set_default_output_folder(all_folders[0]['id'])
                print(f"✓ Set default folder: {all_folders[0]['name']}", file=sys.stderr)
    except Exception as e:
        print(f"⚠️  Error ensuring predefined folders: {e}", file=sys.stderr)

@settings_bp.route('/settings/output-folders', methods=['GET'])
def get_output_folders():
    """Get all output folders (auto-initializes predefined folders)"""
    try:
        # Ensure predefined folders exist
        ensure_predefined_folders()

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
    """Browse filesystem folders (Railway: shows predefined Dropbox folders)"""
    try:
        # On Railway: Show predefined Dropbox folders only
        if IS_RAILWAY:
            print("✓ Railway detected - showing predefined Dropbox folders", file=sys.stderr)

            # Create a virtual folder structure
            folders = []
            for folder in PREDEFINED_FOLDERS:
                folders.append({
                    'name': folder['name'],
                    'path': folder['path'],
                    'isDir': True,
                    'description': folder.get('description', '')
                })

            return jsonify({
                'currentPath': DROPBOX_OUTPUT_BASE,
                'parentPath': None,
                'folders': folders,
                'isRailway': True,
                'message': 'Using predefined Dropbox folders (Railway environment)'
            })

        # Local: Normal filesystem browser
        path = request.args.get('path', os.path.expanduser('~/Downloads'))
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
            'folders': entries,
            'isRailway': False
        })
    except Exception as e:
        print(f"Error browsing folders: {e}", file=sys.stderr)
        return jsonify({'error': str(e)}), 500
