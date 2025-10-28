"""
Database Manager using SQLAlchemy

PRIMARY DATABASE: PostgreSQL on Railway (shared between local and online)
FALLBACK: SQLite (nur für Development ohne DATABASE_URL)

WICHTIG: In Production wird IMMER PostgreSQL verwendet!
SQLite dient nur als Notfall-Fallback für lokale Entwicklung.
"""
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, TIMESTAMP, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')
load_dotenv()

Base = declarative_base()

class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    tts_voice = Column(String(100), default='de-DE-KatjaNeural')
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())
    background_music_path = Column(Text)
    target_language = Column(String(10), default='auto')
    background_music_volume = Column(Integer, default=7)
    video_speed = Column(Float, default=1.0)
    ai_image_model = Column(String(50), default='flux-dev')

    scenes = relationship("Scene", back_populates="project", cascade="all, delete-orphan")

class Scene(Base):
    __tablename__ = 'scenes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    scene_order = Column(Integer, nullable=False)
    script = Column(Text, nullable=False)
    duration = Column(Float, default=5.0)
    background_type = Column(String(50), default='solid')
    background_value = Column(Text)
    audio_path = Column(Text)
    image_path = Column(Text)
    effect_zoom = Column(String(50), default='none')
    effect_pan = Column(String(50), default='none')
    effect_speed = Column(Float, default=1.0)
    effect_shake = Column(Integer, default=0)
    effect_fade = Column(String(50), default='none')
    effect_intensity = Column(Float, default=0.5)
    # New effects (added to fix Creative/Motion effects not saving)
    effect_rotate = Column(String(50), default='none')
    effect_bounce = Column(Integer, default=0)
    effect_tilt_3d = Column(String(50), default='none')
    effect_vignette = Column(String(50), default='none')  # FIXED: Was Integer, should be String
    effect_color_temp = Column(String(50), default='none')  # FIXED: Was Integer, should be String
    effect_saturation = Column(Float, default=1.0)  # 1.0 = FFmpeg direct value (100% saturation = normal)
    effect_film_grain = Column(Integer, default=0)
    effect_glitch = Column(Integer, default=0)
    effect_chromatic = Column(Integer, default=0)
    effect_blur = Column(String(50), default='none')
    effect_light_leaks = Column(Integer, default=0)
    effect_lens_flare = Column(Integer, default=0)
    effect_kaleidoscope = Column(Integer, default=0)
    # Sound effects
    sound_effect_path = Column(Text)
    sound_effect_volume = Column(Integer, default=100)
    sound_effect_offset = Column(Float, default=0.0)
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())

    project = relationship("Project", back_populates="scenes")

class DatabaseManager:
    def __init__(self, db_url=None):
        if db_url is None:
            # Try to get DATABASE_URL from environment
            db_url = os.getenv('DATABASE_URL')

            if not db_url:
                # Fallback to SQLite
                base_dir = os.path.dirname(os.path.abspath(__file__))
                db_path = os.path.join(base_dir, 'editor_projects.db')
                db_url = f'sqlite:///{db_path}'

        self.engine = create_engine(db_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)

    def init_db(self):
        """Initialize database with required tables"""
        Base.metadata.create_all(self.engine)

        # Run one-time migration for existing flux-schnell projects
        session = self.Session()
        try:
            updated = session.query(Project).filter(
                (Project.ai_image_model == 'flux-schnell') |
                (Project.ai_image_model == None)
            ).update(
                {Project.ai_image_model: 'flux-dev'},
                synchronize_session='fetch'
            )
            session.commit()
            if updated > 0:
                print(f"✅ Migrated {updated} projects from flux-schnell to flux-dev")
        except Exception as e:
            print(f"Migration warning: {e}")
            session.rollback()
        finally:
            session.close()

        # Add new effect columns to scenes table (one-time migration)
        from sqlalchemy import text
        session = self.Session()
        try:
            # Check if columns exist by trying to add them
            new_columns = [
                ("effect_rotate", "VARCHAR(50)", "'none'"),
                ("effect_bounce", "INTEGER", "0"),
                ("effect_tilt_3d", "VARCHAR(50)", "'none'"),
                ("effect_vignette", "VARCHAR(50)", "'none'"),  # FIXED: Was INTEGER, needs to be VARCHAR
                ("effect_color_temp", "VARCHAR(50)", "'none'"),  # FIXED: Was INTEGER, needs to be VARCHAR
                ("effect_saturation", "REAL", "1.0"),  # FIXED: Default 1.0 (FFmpeg direct value, 100% = normal)
                ("effect_film_grain", "INTEGER", "0"),
                ("effect_glitch", "INTEGER", "0"),
                ("effect_chromatic", "INTEGER", "0"),
                ("effect_blur", "VARCHAR(50)", "'none'"),
                ("effect_light_leaks", "INTEGER", "0"),
                ("effect_lens_flare", "INTEGER", "0"),
                ("effect_kaleidoscope", "INTEGER", "0"),
                ("sound_effect_path", "TEXT", "NULL"),
                ("sound_effect_volume", "INTEGER", "100"),
                ("sound_effect_offset", "REAL", "0.0"),
            ]

            added_columns = []
            for col_name, col_type, default_val in new_columns:
                try:
                    alter_sql = f"ALTER TABLE scenes ADD COLUMN {col_name} {col_type} DEFAULT {default_val}"
                    session.execute(text(alter_sql))
                    session.commit()
                    added_columns.append(col_name)
                except Exception as col_error:
                    # Column already exists or other error - rollback and continue
                    session.rollback()
                    pass

            if added_columns:
                print(f"✅ Added {len(added_columns)} new effect columns to scenes table: {', '.join(added_columns)}")
        except Exception as e:
            print(f"Migration warning (adding columns): {e}")
            session.rollback()
        finally:
            session.close()

    # Projects
    def create_project(self, name):
        session = self.Session()
        try:
            project = Project(name=name, ai_image_model='flux-dev')
            session.add(project)
            session.commit()
            project_id = project.id
            session.close()
            return self.get_project(project_id)
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def get_project(self, project_id):
        session = self.Session()
        try:
            project = session.query(Project).filter(Project.id == project_id).first()
            if not project:
                return None
            return self._project_to_dict(project)
        finally:
            session.close()

    def list_projects(self):
        session = self.Session()
        try:
            projects = session.query(Project).order_by(Project.updated_at.desc()).all()
            return [self._project_to_dict(p) for p in projects]
        finally:
            session.close()

    def update_project(self, project_id, project_data):
        session = self.Session()
        try:
            project = session.query(Project).filter(Project.id == project_id).first()
            if not project:
                return None

            for key in ['name', 'tts_voice', 'background_music_path', 'target_language',
                        'background_music_volume', 'video_speed', 'ai_image_model']:
                if key in project_data:
                    setattr(project, key, project_data[key])

            project.updated_at = func.now()
            session.commit()
            project_id = project.id
            session.close()
            return self.get_project(project_id)
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def delete_project(self, project_id):
        session = self.Session()
        try:
            project = session.query(Project).filter(Project.id == project_id).first()
            if project:
                session.delete(project)
                session.commit()
            session.close()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def update_project_timestamp(self, project_id):
        session = self.Session()
        try:
            project = session.query(Project).filter(Project.id == project_id).first()
            if project:
                project.updated_at = func.now()
                session.commit()
        except:
            session.rollback()
        finally:
            session.close()

    # Scenes
    def add_scene(self, project_id, scene_data):
        session = self.Session()
        try:
            # Get current max order
            max_order = session.query(func.max(Scene.scene_order)).filter(
                Scene.project_id == project_id
            ).scalar() or 0

            scene = Scene(
                project_id=project_id,
                scene_order=max_order + 1,
                script=scene_data.get('script'),
                duration=scene_data.get('duration', 5.0),
                background_type=scene_data.get('background_type', 'solid'),
                background_value=scene_data.get('background_value', '#000000')
            )
            session.add(scene)
            session.commit()
            scene_id = scene.id
            session.close()

            self.update_project_timestamp(project_id)
            return self.get_scene(scene_id)
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def get_scene(self, scene_id):
        session = self.Session()
        try:
            scene = session.query(Scene).filter(Scene.id == scene_id).first()
            if not scene:
                return None
            return self._scene_to_dict(scene)
        finally:
            session.close()

    def get_project_scenes(self, project_id):
        session = self.Session()
        try:
            scenes = session.query(Scene).filter(
                Scene.project_id == project_id
            ).order_by(Scene.scene_order).all()
            return [self._scene_to_dict(s) for s in scenes]
        finally:
            session.close()

    def update_scene(self, scene_id, scene_data):
        session = self.Session()
        try:
            scene = session.query(Scene).filter(Scene.id == scene_id).first()
            if not scene:
                return None

            for key in ['script', 'duration', 'background_type', 'background_value',
                        'audio_path', 'image_path', 'effect_zoom', 'effect_pan', 'effect_speed',
                        'effect_shake', 'effect_fade', 'effect_intensity',
                        # New effects (added to fix effects not saving)
                        'effect_rotate', 'effect_bounce', 'effect_tilt_3d',
                        'effect_vignette', 'effect_color_temp', 'effect_saturation',
                        'effect_film_grain', 'effect_glitch', 'effect_chromatic', 'effect_blur',
                        'effect_light_leaks', 'effect_lens_flare', 'effect_kaleidoscope',
                        # Sound effects
                        'sound_effect_path', 'sound_effect_volume', 'sound_effect_offset']:
                if key in scene_data:
                    setattr(scene, key, scene_data[key])

            scene.updated_at = func.now()
            session.commit()
            scene_id = scene.id
            project_id = scene.project_id
            session.close()

            self.update_project_timestamp(project_id)
            return self.get_scene(scene_id)
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def delete_scene(self, scene_id):
        session = self.Session()
        try:
            scene = session.query(Scene).filter(Scene.id == scene_id).first()
            if scene:
                project_id = scene.project_id
                session.delete(scene)
                session.commit()
                self.update_project_timestamp(project_id)
                return True
            return False
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def reorder_scenes(self, project_id, scene_orders):
        session = self.Session()
        try:
            for scene_id, new_order in scene_orders.items():
                scene = session.query(Scene).filter(Scene.id == scene_id).first()
                if scene:
                    scene.scene_order = new_order
            session.commit()
            self.update_project_timestamp(project_id)
        except:
            session.rollback()
            raise
        finally:
            session.close()

    # Helper methods
    def _project_to_dict(self, project):
        return {
            'id': project.id,
            'name': project.name,
            'tts_voice': project.tts_voice,
            'created_at': project.created_at.strftime('%Y-%m-%d %H:%M:%S') if project.created_at else None,
            'updated_at': project.updated_at.strftime('%Y-%m-%d %H:%M:%S') if project.updated_at else None,
            'background_music_path': project.background_music_path,
            'target_language': project.target_language,
            'background_music_volume': project.background_music_volume,
            'video_speed': project.video_speed,
            'ai_image_model': project.ai_image_model
        }

    def _scene_to_dict(self, scene):
        return {
            'id': scene.id,
            'project_id': scene.project_id,
            'scene_order': scene.scene_order,
            'script': scene.script,
            'duration': scene.duration,
            'background_type': scene.background_type,
            'background_value': scene.background_value,
            'audio_path': scene.audio_path,
            'image_path': scene.image_path,
            'effect_zoom': scene.effect_zoom,
            'effect_pan': scene.effect_pan,
            'effect_speed': scene.effect_speed,
            'effect_shake': scene.effect_shake,
            'effect_fade': scene.effect_fade,
            'effect_intensity': scene.effect_intensity,
            # New effects (added to fix Creative/Motion effects not being returned)
            'effect_rotate': getattr(scene, 'effect_rotate', 'none'),
            'effect_bounce': getattr(scene, 'effect_bounce', 0),
            'effect_tilt_3d': getattr(scene, 'effect_tilt_3d', 'none'),
            'effect_vignette': getattr(scene, 'effect_vignette', 'none'),  # FIXED: Default 'none' instead of 0
            'effect_color_temp': getattr(scene, 'effect_color_temp', 'none'),  # FIXED: Default 'none' instead of 0
            'effect_saturation': getattr(scene, 'effect_saturation', 1.0),  # FIXED: Default 1.0 (FFmpeg direct, 100% = normal)
            'effect_film_grain': getattr(scene, 'effect_film_grain', 0),
            'effect_glitch': getattr(scene, 'effect_glitch', 0),
            'effect_chromatic': getattr(scene, 'effect_chromatic', 0),
            'effect_blur': getattr(scene, 'effect_blur', 'none'),
            'effect_light_leaks': getattr(scene, 'effect_light_leaks', 0),
            'effect_lens_flare': getattr(scene, 'effect_lens_flare', 0),
            'effect_kaleidoscope': getattr(scene, 'effect_kaleidoscope', 0),
            # Sound effects
            'sound_effect_path': getattr(scene, 'sound_effect_path', None),
            'sound_effect_volume': getattr(scene, 'sound_effect_volume', 100),
            'sound_effect_offset': getattr(scene, 'sound_effect_offset', 0.0),
            'created_at': scene.created_at.strftime('%Y-%m-%d %H:%M:%S') if scene.created_at else None,
            'updated_at': scene.updated_at.strftime('%Y-%m-%d %H:%M:%S') if scene.updated_at else None
        }
