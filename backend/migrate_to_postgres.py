#!/usr/bin/env python3
"""
Migration Script: SQLite → PostgreSQL
Migriert alle Projekte und Szenen von der lokalen SQLite DB zur Railway PostgreSQL DB
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
base_dir = Path(__file__).parent
load_dotenv(base_dir / '.env.local')

# Import both database managers
sys.path.insert(0, str(base_dir / 'database'))

# Import old SQLite manager
import importlib.util
spec = importlib.util.spec_from_file_location("sqlite_manager", base_dir / "database" / "db_manager_sqlite_backup.py")
sqlite_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sqlite_module)
SQLiteDatabaseManager = sqlite_module.DatabaseManager

# Import new SQLAlchemy manager
from database.db_manager import DatabaseManager as PostgreSQLDatabaseManager

def migrate_data():
    """Migriert alle Daten von SQLite nach PostgreSQL"""

    print("=" * 60)
    print("🔄 MIGRATION: SQLite → PostgreSQL")
    print("=" * 60)

    # 1. Verbinde zu SQLite (alte DB)
    print("\n📂 Verbinde zu SQLite...")
    sqlite_db = SQLiteDatabaseManager()

    # 2. Verbinde zu PostgreSQL (neue DB)
    print("🐘 Verbinde zu PostgreSQL...")
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ ERROR: DATABASE_URL nicht gefunden in .env.local!")
        return False

    print(f"   URL: {database_url[:30]}...{database_url[-20:]}")
    postgres_db = PostgreSQLDatabaseManager(db_url=database_url)

    # 3. Lösche und erstelle PostgreSQL Tabellen neu (sauberer Start)
    print("\n🔧 Bereite PostgreSQL vor...")
    from sqlalchemy import inspect
    inspector = inspect(postgres_db.engine)
    existing_tables = inspector.get_table_names()

    if existing_tables:
        print(f"   🗑️  Lösche existierende Tabellen: {existing_tables}")
        from database.db_manager import Base
        Base.metadata.drop_all(postgres_db.engine)
        print("   ✅ Alte Tabellen gelöscht")

    print("   🔧 Erstelle neue Tabellen...")
    postgres_db.init_db()
    print("   ✅ Tabellen erstellt")

    # 4. Lade alle Projekte aus SQLite
    print("\n📊 Lade Projekte aus SQLite...")
    projects = sqlite_db.list_projects()
    print(f"   Gefunden: {len(projects)} Projekte")

    if not projects:
        print("   ⚠️  Keine Projekte gefunden - nichts zu migrieren")
        return True

    # 5. Migriere jedes Projekt
    print("\n🚀 Starte Migration...")
    migrated_projects = 0
    migrated_scenes = 0

    for project in projects:
        project_id = project['id']
        project_name = project['name']

        print(f"\n   📁 Projekt {project_id}: {project_name}")

        # Erstelle Projekt in PostgreSQL
        new_project = postgres_db.create_project(project_name)
        new_project_id = new_project['id']

        # Update alle Projekt-Felder
        update_data = {
            'ai_image_model': project.get('ai_image_model', 'flux-dev'),
            'ai_voice': project.get('ai_voice'),
            'subtitles_enabled': project.get('subtitles_enabled', 0),
            'logo_path': project.get('logo_path'),
            'logo_position': project.get('logo_position', 'bottom-right'),
            'logo_scale': project.get('logo_scale', 1.0),
            'music_path': project.get('music_path'),
            'music_volume': project.get('music_volume', 0.5),
            'output_path': project.get('output_path')
        }
        postgres_db.update_project(new_project_id, update_data)
        migrated_projects += 1

        # Lade Szenen für dieses Projekt
        scenes = sqlite_db.get_project_scenes(project_id)
        print(f"      → {len(scenes)} Szenen")

        # Migriere alle Szenen
        for idx, scene in enumerate(scenes):
            # Robuste Datenmapping - SQLite und PostgreSQL verwenden gleiche Feldnamen!
            scene_data = {
                'scene_order': scene.get('scene_order', idx + 1),  # Fallback zu Index + 1
                'script': scene.get('script', ''),  # Fallback zu leerem String für NOT NULL constraint
                'duration': scene.get('duration', 5.0),
                'background_type': scene.get('background_type', 'solid'),
                'background_value': scene.get('background_value'),
                'audio_path': scene.get('audio_path'),
                'effect_zoom': scene.get('effect_zoom', 'none'),
                'effect_pan': scene.get('effect_pan', 'none'),
                'effect_speed': scene.get('effect_speed', 1.0),
                'effect_shake': scene.get('effect_shake', 0),
                'effect_fade': scene.get('effect_fade', 'none'),
                'effect_intensity': scene.get('effect_intensity', 0.5)
            }
            try:
                postgres_db.add_scene(new_project_id, scene_data)  # project_id als separates Argument
                migrated_scenes += 1
            except Exception as e:
                print(f"      ⚠️  Warnung: Szene {scene.get('id', '?')} konnte nicht migriert werden: {e}")

    # 6. Zusammenfassung
    print("\n" + "=" * 60)
    print("✅ MIGRATION ABGESCHLOSSEN!")
    print("=" * 60)
    print(f"   Projekte migriert: {migrated_projects}")
    print(f"   Szenen migriert:   {migrated_scenes}")

    # 7. Verifikation
    print("\n🔍 Verifikation...")
    postgres_projects = postgres_db.list_projects()
    print(f"   PostgreSQL Projekte: {len(postgres_projects)}")

    if len(postgres_projects) == len(projects):
        print("   ✅ Alle Projekte erfolgreich migriert!")
        return True
    else:
        print(f"   ⚠️  Warnung: Anzahl unterschiedlich (SQLite: {len(projects)}, PostgreSQL: {len(postgres_projects)})")
        return False

if __name__ == '__main__':
    try:
        success = migrate_data()
        if success:
            print("\n🎉 Migration erfolgreich! Du kannst jetzt den Server mit PostgreSQL starten.")
            sys.exit(0)
        else:
            print("\n⚠️  Migration mit Warnungen abgeschlossen. Bitte überprüfen!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ FEHLER während Migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
