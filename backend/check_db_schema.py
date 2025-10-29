#!/usr/bin/env python3
"""
Prüft das aktuelle Datenbank-Schema
NUR LESEN, KEINE ÄNDERUNGEN!
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text

# Load environment variables (same order as db_manager.py)
base_dir = Path(__file__).parent
load_dotenv(base_dir / '.env.local')
load_dotenv(base_dir / '.env')

def check_database():
    """Analysiert welche DB verwendet wird und das Schema"""

    print("=" * 80)
    print("🔍 DATENBANK-ANALYSE (NUR LESEN)")
    print("=" * 80)

    # 1. Welche DATABASE_URL wird verwendet?
    db_url = os.getenv('DATABASE_URL')

    print("\n📍 DATENBANK-KONFIGURATION:")
    if db_url:
        # Maskiere Passwort für Ausgabe
        safe_url = db_url.split('@')[0].split(':')
        safe_url = f"{safe_url[0]}:***@" + db_url.split('@')[1]
        print(f"   DATABASE_URL gefunden: {safe_url}")

        if 'postgresql' in db_url:
            print("   ✅ Typ: PostgreSQL (Railway)")
        elif 'sqlite' in db_url:
            print("   ⚠️  Typ: SQLite (Fallback)")
    else:
        print("   ❌ Keine DATABASE_URL gefunden!")
        db_path = os.path.join(base_dir, 'database', 'editor_projects.db')
        db_url = f'sqlite:///{db_path}'
        print(f"   📁 Fallback zu SQLite: {db_path}")

    # 2. Verbinde und inspiziere Schema
    print("\n🔌 VERBINDE ZU DATENBANK...")
    try:
        engine = create_engine(db_url, echo=False)
        inspector = inspect(engine)

        # 3. Tabellen auflisten
        tables = inspector.get_table_names()
        print(f"\n📊 TABELLEN GEFUNDEN: {len(tables)}")
        for table in tables:
            print(f"   - {table}")

        # 4. Scenes Tabelle detailliert analysieren
        if 'scenes' in tables:
            print("\n🎬 SCENES TABELLE - SCHEMA DETAILS:")
            columns = inspector.get_columns('scenes')

            # Fokus auf effect columns
            effect_columns = [col for col in columns if col['name'].startswith('effect_')]

            print(f"\n   Gesamt Columns: {len(columns)}")
            print(f"   Effect Columns: {len(effect_columns)}")

            print("\n   🔍 EFFECT COLUMNS (relevant für Bug):")
            for col in effect_columns:
                col_name = col['name']
                col_type = str(col['type'])
                default = col.get('default', 'NULL')

                # Markiere die problematischen Columns
                if col_name in ['effect_vignette', 'effect_color_temp', 'effect_saturation']:
                    marker = " ⚠️  KRITISCH!" if col_name in ['effect_vignette', 'effect_color_temp'] else " ✅ OK"
                    print(f"   • {col_name:25} {col_type:20} default={default}{marker}")
                else:
                    print(f"   • {col_name:25} {col_type:20} default={default}")

        # 5. Daten-Check
        if 'projects' in tables and 'scenes' in tables:
            with engine.connect() as conn:
                # Projekte zählen
                result = conn.execute(text("SELECT COUNT(*) FROM projects"))
                project_count = result.scalar()

                # Scenes zählen
                result = conn.execute(text("SELECT COUNT(*) FROM scenes"))
                scene_count = result.scalar()

                print(f"\n📈 DATEN:")
                print(f"   Projekte: {project_count}")
                print(f"   Scenes:   {scene_count}")

                # Sample effect values
                if scene_count > 0:
                    result = conn.execute(text("""
                        SELECT
                            id,
                            effect_vignette,
                            effect_color_temp,
                            effect_saturation
                        FROM scenes
                        LIMIT 5
                    """))

                    print(f"\n   📝 SAMPLE EFFECT VALUES (erste 5 Scenes):")
                    for row in result:
                        print(f"   Scene {row[0]}: vignette={row[1]}, color_temp={row[2]}, saturation={row[3]}")

        print("\n" + "=" * 80)
        print("✅ ANALYSE ABGESCHLOSSEN")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ FEHLER beim Analysieren: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == '__main__':
    try:
        check_database()
    except KeyboardInterrupt:
        print("\n\n⚠️  Abgebrochen durch Benutzer")
        sys.exit(1)
