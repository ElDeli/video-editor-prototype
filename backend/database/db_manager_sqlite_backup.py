import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path=None):
        if db_path is None:
            # Use absolute path relative to THIS file's location
            base_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.getenv('DATABASE_PATH', os.path.join(base_dir, 'editor_projects.db'))
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initialize database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                tts_voice TEXT DEFAULT 'de-DE-KatjaNeural',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Add tts_voice column to existing projects tables (migration)
        try:
            cursor.execute("ALTER TABLE projects ADD COLUMN tts_voice TEXT DEFAULT 'de-DE-KatjaNeural'")
            conn.commit()
        except sqlite3.OperationalError:
            # Column already exists
            pass

        # Add background_music_path column to existing projects tables (migration)
        try:
            cursor.execute("ALTER TABLE projects ADD COLUMN background_music_path TEXT")
            conn.commit()
        except sqlite3.OperationalError:
            # Column already exists
            pass

        # Add target_language column to existing projects tables (migration)
        try:
            cursor.execute("ALTER TABLE projects ADD COLUMN target_language TEXT DEFAULT 'auto'")
            conn.commit()
        except sqlite3.OperationalError:
            # Column already exists
            pass

        # Add background_music_volume column to existing projects tables (migration)
        try:
            cursor.execute("ALTER TABLE projects ADD COLUMN background_music_volume INTEGER DEFAULT 7")
            conn.commit()
        except sqlite3.OperationalError:
            # Column already exists
            pass

        # Add video_speed column to existing projects tables (migration)
        try:
            cursor.execute("ALTER TABLE projects ADD COLUMN video_speed REAL DEFAULT 1.0")
            conn.commit()
        except sqlite3.OperationalError:
            # Column already exists
            pass

        # Add ai_image_model column to existing projects tables (migration)
        try:
            cursor.execute("ALTER TABLE projects ADD COLUMN ai_image_model TEXT DEFAULT 'flux-dev'")
            conn.commit()
        except sqlite3.OperationalError:
            # Column already exists
            pass

        # Update existing projects that use flux-schnell to flux-dev (one-time migration)
        try:
            cursor.execute("UPDATE projects SET ai_image_model = 'flux-dev' WHERE ai_image_model = 'flux-schnell' OR ai_image_model IS NULL")
            conn.commit()
        except sqlite3.OperationalError:
            pass

        # Settings table for output folders
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Output folders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS output_folders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                is_default INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Scenes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scenes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                scene_order INTEGER NOT NULL,
                script TEXT NOT NULL,
                duration REAL DEFAULT 5.0,
                background_type TEXT DEFAULT 'solid',
                background_value TEXT,
                audio_path TEXT,
                effect_zoom TEXT DEFAULT 'none',
                effect_pan TEXT DEFAULT 'none',
                effect_speed REAL DEFAULT 1.0,
                effect_shake INTEGER DEFAULT 0,
                effect_fade TEXT DEFAULT 'none',
                effect_intensity REAL DEFAULT 0.5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        ''')

        # Add effect columns to existing scenes tables (migration)
        effect_columns = [
            ("effect_zoom", "TEXT DEFAULT 'none'"),
            ("effect_pan", "TEXT DEFAULT 'none'"),
            ("effect_speed", "REAL DEFAULT 1.0"),
            ("effect_shake", "INTEGER DEFAULT 0"),
            ("effect_fade", "TEXT DEFAULT 'none'"),
            ("effect_intensity", "REAL DEFAULT 0.5"),
            # New motion effects
            ("effect_rotate", "TEXT DEFAULT 'none'"),
            ("effect_bounce", "INTEGER DEFAULT 0"),
            ("effect_tilt_3d", "TEXT DEFAULT 'none'"),
            # New color effects
            ("effect_vignette", "TEXT DEFAULT 'none'"),
            ("effect_color_temp", "TEXT DEFAULT 'none'"),
            ("effect_saturation", "REAL DEFAULT 1.0"),
            # New creative effects
            ("effect_film_grain", "INTEGER DEFAULT 0"),
            ("effect_glitch", "INTEGER DEFAULT 0"),
            ("effect_chromatic", "INTEGER DEFAULT 0"),
            ("effect_blur", "TEXT DEFAULT 'none'"),
            ("effect_light_leaks", "INTEGER DEFAULT 0"),
            ("effect_lens_flare", "INTEGER DEFAULT 0"),
            ("effect_kaleidoscope", "INTEGER DEFAULT 0"),
            # Sound effects
            ("sound_effect_path", "TEXT"),
            ("sound_effect_volume", "INTEGER DEFAULT 50"),  # Volume 0-100%
            ("sound_effect_offset", "INTEGER DEFAULT 0")    # Timing offset 0-100%
        ]

        for col_name, col_type in effect_columns:
            try:
                cursor.execute(f"ALTER TABLE scenes ADD COLUMN {col_name} {col_type}")
                conn.commit()
            except sqlite3.OperationalError:
                # Column already exists
                pass

        # Create index on project_id and scene_order
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_scenes_project_order
            ON scenes(project_id, scene_order)
        ''')

        conn.commit()
        conn.close()

    # Projects
    def create_project(self, name):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO projects (name, ai_image_model) VALUES (?, ?)',
            (name, 'flux-dev')
        )
        project_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return self.get_project(project_id)

    def get_project(self, project_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def list_projects(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM projects ORDER BY updated_at DESC')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def update_project_timestamp(self, project_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (project_id,)
        )
        conn.commit()
        conn.close()

    def update_project(self, project_id, project_data):
        """Update project settings"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Build update query dynamically
        fields = []
        values = []
        for key in ['tts_voice', 'background_music_path', 'background_music_volume', 'target_language', 'video_speed', 'ai_image_model']:
            if key in project_data:
                fields.append(f'{key} = ?')
                values.append(project_data[key])

        if fields:
            fields.append('updated_at = CURRENT_TIMESTAMP')
            values.append(project_id)
            query = f'UPDATE projects SET {", ".join(fields)} WHERE id = ?'
            cursor.execute(query, values)
            conn.commit()

        conn.close()
        return self.get_project(project_id)

    def delete_project(self, project_id):
        """Delete a project and all its scenes"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Delete all scenes first (foreign key constraint)
        cursor.execute('DELETE FROM scenes WHERE project_id = ?', (project_id,))

        # Delete the project
        cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))

        conn.commit()
        conn.close()

    # Scenes
    def add_scene(self, project_id, scene_data):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Get current max order
        cursor.execute(
            'SELECT MAX(scene_order) FROM scenes WHERE project_id = ?',
            (project_id,)
        )
        max_order = cursor.fetchone()[0]
        scene_order = (max_order or 0) + 1

        cursor.execute('''
            INSERT INTO scenes (
                project_id, scene_order, script, duration,
                background_type, background_value
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            project_id,
            scene_order,
            scene_data.get('script'),
            scene_data.get('duration', 5.0),
            scene_data.get('background_type', 'solid'),
            scene_data.get('background_value', '#000000')
        ))

        scene_id = cursor.lastrowid
        conn.commit()
        conn.close()

        self.update_project_timestamp(project_id)
        return self.get_scene(scene_id)

    def get_scene(self, scene_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM scenes WHERE id = ?', (scene_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_project_scenes(self, project_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM scenes WHERE project_id = ? ORDER BY scene_order',
            (project_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        # DEBUG: Print raw row data
        import sys
        result = []
        for row in rows:
            scene_dict = dict(row)
            # Log sound effect info for debugging
            if scene_dict.get('sound_effect_path'):
                print(f"[DB] Scene {scene_dict['id']} has sound_effect_path: {scene_dict['sound_effect_path']}", file=sys.stderr, flush=True)
            result.append(scene_dict)

        return result

    def update_scene(self, scene_id, scene_data):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Build update query dynamically
        fields = []
        values = []
        allowed_fields = [
            'script', 'duration', 'background_type', 'background_value', 'audio_path',
            'effect_zoom', 'effect_pan', 'effect_speed', 'effect_shake',
            'effect_fade', 'effect_intensity',
            # New motion effects
            'effect_rotate', 'effect_bounce', 'effect_tilt_3d',
            # New color effects
            'effect_vignette', 'effect_color_temp', 'effect_saturation',
            # New creative effects
            'effect_film_grain', 'effect_glitch', 'effect_chromatic', 'effect_blur',
            'effect_light_leaks', 'effect_lens_flare', 'effect_kaleidoscope',
            # Sound effects
            'sound_effect_path', 'sound_effect_volume', 'sound_effect_offset'
        ]

        for key in allowed_fields:
            if key in scene_data:
                fields.append(f'{key} = ?')
                values.append(scene_data[key])

        if fields:
            fields.append('updated_at = CURRENT_TIMESTAMP')
            values.append(scene_id)
            query = f'UPDATE scenes SET {", ".join(fields)} WHERE id = ?'
            cursor.execute(query, values)
            conn.commit()

        # Get project_id to update timestamp
        cursor.execute('SELECT project_id FROM scenes WHERE id = ?', (scene_id,))
        project_id = cursor.fetchone()[0]
        conn.close()

        self.update_project_timestamp(project_id)
        return self.get_scene(scene_id)

    def delete_scene(self, scene_id):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Get project_id and scene_order
        cursor.execute(
            'SELECT project_id, scene_order FROM scenes WHERE id = ?',
            (scene_id,)
        )
        row = cursor.fetchone()
        if not row:
            conn.close()
            return False

        project_id, scene_order = row[0], row[1]

        # Delete scene
        cursor.execute('DELETE FROM scenes WHERE id = ?', (scene_id,))

        # Reorder remaining scenes
        cursor.execute('''
            UPDATE scenes
            SET scene_order = scene_order - 1
            WHERE project_id = ? AND scene_order > ?
        ''', (project_id, scene_order))

        conn.commit()
        conn.close()

        self.update_project_timestamp(project_id)
        return True

    def reorder_scenes(self, project_id, scene_ids):
        """Reorder scenes based on array of scene IDs"""
        conn = self.get_connection()
        cursor = conn.cursor()

        for order, scene_id in enumerate(scene_ids, start=1):
            cursor.execute(
                'UPDATE scenes SET scene_order = ? WHERE id = ? AND project_id = ?',
                (order, scene_id, project_id)
            )

        conn.commit()
        conn.close()
        self.update_project_timestamp(project_id)

    # Output Folders Management
    def get_output_folders(self):
        """Get all output folders"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM output_folders ORDER BY is_default DESC, name ASC')
        folders = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return folders

    def add_output_folder(self, name, path):
        """Add new output folder"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO output_folders (name, path, is_default)
            VALUES (?, ?, 0)
        ''', (name, path))

        folder_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return self.get_output_folder(folder_id)

    def get_output_folder(self, folder_id):
        """Get output folder by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM output_folders WHERE id = ?', (folder_id,))
        folder = cursor.fetchone()
        conn.close()
        return dict(folder) if folder else None

    def delete_output_folder(self, folder_id):
        """Delete output folder"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM output_folders WHERE id = ?', (folder_id,))
        conn.commit()
        conn.close()

    def set_default_output_folder(self, folder_id):
        """Set default output folder"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Remove default from all folders
        cursor.execute('UPDATE output_folders SET is_default = 0')

        # Set new default
        cursor.execute('UPDATE output_folders SET is_default = 1 WHERE id = ?', (folder_id,))

        conn.commit()
        conn.close()

    def get_default_output_folder(self):
        """Get default output folder"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM output_folders WHERE is_default = 1 LIMIT 1')
        folder = cursor.fetchone()
        conn.close()
        return dict(folder) if folder else None
