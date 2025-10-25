from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables FIRST before any other imports
load_dotenv()

from database.db_manager import DatabaseManager
from api.projects import projects_bp
from api.scenes import scenes_bp
from api.scripts import scripts_bp
from api.tts import tts_bp
from api.uploads import uploads_bp
from api.sound_effects import sound_effects_bp
from api.music import music_bp
from api.settings import settings_bp

app = Flask(__name__)

# Configure CORS for iframe embedding + direct access
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://app.momentummind.de",
            "https://video-editor.momentummind.de",
            "https://video-editor-prototype-production.up.railway.app",
            "http://localhost:3000",
            "http://localhost:8080"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Initialize database
db_manager = DatabaseManager()
db_manager.init_db()

# Register blueprints
app.register_blueprint(projects_bp, url_prefix='/api')
app.register_blueprint(scenes_bp, url_prefix='/api')
app.register_blueprint(scripts_bp, url_prefix='/api')
app.register_blueprint(tts_bp, url_prefix='/api')
app.register_blueprint(uploads_bp, url_prefix='/api')
app.register_blueprint(sound_effects_bp, url_prefix='/api')
app.register_blueprint(music_bp, url_prefix='/api')
app.register_blueprint(settings_bp, url_prefix='/api')

@app.route('/')
def serve_frontend():
    """Serve the React frontend"""
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files (JS, CSS, etc.)"""
    if path and os.path.exists(os.path.join('static', path)):
        return send_from_directory('static', path)
    # If file doesn't exist, serve index.html (for React Router)
    return send_from_directory('static', 'index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Video Editor API is running'})

@app.route('/api/previews/<filename>', methods=['GET'])
def serve_preview(filename):
    """Serve generated preview videos"""
    # Try Dropbox location first (Mac local environment)
    dropbox_previews_dir = Path(os.path.expanduser('~/Dropbox/Apps/output Horoskop/video_editor_prototype/previews'))

    if dropbox_previews_dir.exists() and (dropbox_previews_dir / filename).exists():
        return send_from_directory(dropbox_previews_dir, filename)

    # Fallback to local backend/previews (Railway environment)
    local_previews_dir = Path('./previews')
    if local_previews_dir.exists() and (local_previews_dir / filename).exists():
        return send_from_directory(local_previews_dir, filename)

    return jsonify({'error': 'Preview video not found'}), 404

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    # Disable reloader to prevent multiprocessing crashes
    app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)
