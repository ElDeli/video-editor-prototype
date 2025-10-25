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
CORS(app)

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

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Video Editor API is running'})

@app.route('/api/previews/<filename>', methods=['GET'])
def serve_preview(filename):
    """Serve generated preview videos from centralized Dropbox location"""
    previews_dir = Path(os.path.expanduser('~/Dropbox/Apps/output Horoskop/video_editor_prototype/previews'))
    return send_from_directory(previews_dir, filename)

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
