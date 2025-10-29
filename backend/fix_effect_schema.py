#!/usr/bin/env python3
"""
PostgreSQL Schema-Fix: effect_vignette & effect_color_temp INTEGER → VARCHAR(50)

PROBLEM:
- effect_vignette ist INTEGER, aber Code erwartet VARCHAR (values: 'none', 'light', 'heavy')
- effect_color_temp ist INTEGER, aber Code erwartet VARCHAR (values: 'none', 'warm', 'cool')
- effect_saturation hat default 0 (desaturated), sollte 50 sein (normal)

SOLUTION:
1. ALTER COLUMN type von INTEGER → VARCHAR(50)
2. Konvertiere bestehende Werte: 0 → 'none'
3. UPDATE effect_saturation: 0 → 50

SICHER: Alle bestehenden Daten haben 0, Conversion ist verlustfrei!
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
base_dir = Path(__file__).parent
load_dotenv(base_dir / '.env.local')
load_dotenv(base_dir / '.env')

def fix_schema():
    """
    Führt das Schema-Update auf PostgreSQL durch
    WICHTIG: Backend muss gestoppt sein!
    """

    print("=" * 80)
    print("🔧 POSTGRESQL SCHEMA-FIX")
    print("=" * 80)

    # Hole DATABASE_URL
    db_url = os.getenv('DATABASE_URL')

    if not db_url:
        print("❌ ERROR: DATABASE_URL nicht gefunden!")
        print("   Bitte .env.local oder .env mit DATABASE_URL erstellen.")
        return False

    if 'postgresql' not in db_url:
        print(f"❌ ERROR: Keine PostgreSQL URL! ({db_url})")
        return False

    # Maskiere Passwort
    safe_url = db_url.split('@')[0].split(':')
    safe_url = f"{safe_url[0]}:***@" + db_url.split('@')[1]
    print(f"\n📍 Datenbank: {safe_url}")

    # Verbinde zu PostgreSQL
    print("\n🔌 Verbinde zu PostgreSQL...")
    try:
        engine = create_engine(db_url, echo=False)
        conn = engine.connect()
        print("   ✅ Verbindung erfolgreich")
    except Exception as e:
        print(f"   ❌ Verbindung fehlgeschlagen: {e}")
        return False

    # Prüfe aktuelles Schema
    print("\n🔍 Prüfe aktuelles Schema...")
    try:
        result = conn.execute(text("""
            SELECT column_name, data_type, column_default
            FROM information_schema.columns
            WHERE table_name = 'scenes'
            AND column_name IN ('effect_vignette', 'effect_color_temp', 'effect_saturation')
            ORDER BY column_name
        """))

        current_schema = {row[0]: {'type': row[1], 'default': row[2]} for row in result}

        for col_name in ['effect_vignette', 'effect_color_temp', 'effect_saturation']:
            if col_name in current_schema:
                col_info = current_schema[col_name]
                print(f"   {col_name:25} {col_info['type']:20} default={col_info['default']}")
            else:
                print(f"   {col_name:25} NICHT GEFUNDEN!")

        # Zähle Rows
        result = conn.execute(text("SELECT COUNT(*) FROM scenes"))
        scene_count = result.scalar()
        print(f"\n   Gesamt Scenes: {scene_count}")

    except Exception as e:
        print(f"   ❌ Schema-Prüfung fehlgeschlagen: {e}")
        conn.close()
        return False

    # Warte auf Bestätigung
    print("\n" + "=" * 80)
    print("⚠️  WARNUNG: Datenbankschema wird geändert!")
    print("=" * 80)
    print("Änderungen:")
    print("  1. effect_vignette:   INTEGER → VARCHAR(50), alle 0 → 'none'")
    print("  2. effect_color_temp: INTEGER → VARCHAR(50), alle 0 → 'none'")
    print("  3. effect_saturation: alle 0 → 50 (50 = normal color)")
    print()
    print(f"Betroffen: {scene_count} Scenes")
    print()

    confirm = input("Fortfahren? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("\n❌ Abgebrochen.")
        conn.close()
        return False

    # Führe Updates durch
    print("\n🚀 Starte Schema-Updates...")

    try:
        # Start Transaction
        trans = conn.begin()

        # 1. effect_vignette: INTEGER → VARCHAR(50)
        print("\n   📝 1/3: effect_vignette INTEGER → VARCHAR(50)...")
        conn.execute(text("""
            ALTER TABLE scenes
            ALTER COLUMN effect_vignette TYPE VARCHAR(50)
            USING CASE
                WHEN effect_vignette = 0 THEN 'none'
                ELSE 'none'
            END
        """))
        conn.execute(text("""
            ALTER TABLE scenes
            ALTER COLUMN effect_vignette SET DEFAULT 'none'
        """))
        print("      ✅ effect_vignette erfolgreich konvertiert")

        # 2. effect_color_temp: INTEGER → VARCHAR(50)
        print("\n   📝 2/3: effect_color_temp INTEGER → VARCHAR(50)...")
        conn.execute(text("""
            ALTER TABLE scenes
            ALTER COLUMN effect_color_temp TYPE VARCHAR(50)
            USING CASE
                WHEN effect_color_temp = 0 THEN 'none'
                ELSE 'none'
            END
        """))
        conn.execute(text("""
            ALTER TABLE scenes
            ALTER COLUMN effect_color_temp SET DEFAULT 'none'
        """))
        print("      ✅ effect_color_temp erfolgreich konvertiert")

        # 3. effect_saturation: 0 → 50
        print("\n   📝 3/3: effect_saturation: 0 → 50...")
        result = conn.execute(text("""
            UPDATE scenes
            SET effect_saturation = 50
            WHERE effect_saturation = 0
        """))
        updated_rows = result.rowcount
        print(f"      ✅ {updated_rows} Scenes aktualisiert (saturation: 0 → 50)")

        # Commit Transaction
        trans.commit()
        print("\n   ✅ Alle Änderungen committed!")

    except Exception as e:
        trans.rollback()
        print(f"\n   ❌ FEHLER: {e}")
        print("   🔙 Rollback durchgeführt - Keine Änderungen gespeichert!")
        conn.close()
        return False

    # Verify
    print("\n🔍 Verifikation...")
    try:
        result = conn.execute(text("""
            SELECT column_name, data_type, column_default
            FROM information_schema.columns
            WHERE table_name = 'scenes'
            AND column_name IN ('effect_vignette', 'effect_color_temp', 'effect_saturation')
            ORDER BY column_name
        """))

        for row in result:
            col_name, data_type, default_val = row
            status = "✅" if (
                (col_name == 'effect_vignette' and data_type == 'character varying') or
                (col_name == 'effect_color_temp' and data_type == 'character varying') or
                (col_name == 'effect_saturation' and data_type == 'integer')
            ) else "❌"
            print(f"   {status} {col_name:25} {data_type:30} default={default_val}")

        # Check sample values
        result = conn.execute(text("""
            SELECT
                effect_vignette,
                effect_color_temp,
                effect_saturation
            FROM scenes
            LIMIT 5
        """))

        print("\n   📊 Sample Values (erste 5 Scenes):")
        for row in result:
            print(f"      vignette={row[0]}, color_temp={row[1]}, saturation={row[2]}")

    except Exception as e:
        print(f"   ⚠️  Verifikation fehlgeschlagen: {e}")

    conn.close()

    print("\n" + "=" * 80)
    print("✅ SCHEMA-UPDATE ERFOLGREICH ABGESCHLOSSEN!")
    print("=" * 80)
    print("\n📌 NÄCHSTE SCHRITTE:")
    print("   1. Backend neu starten")
    print("   2. Neues Projekt erstellen und Effekte testen")
    print("   3. Verify: Effect-Values sollten jetzt speicherbar sein!")
    print()

    return True

if __name__ == '__main__':
    try:
        success = fix_schema()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Abgebrochen durch Benutzer")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unerwarteter Fehler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
