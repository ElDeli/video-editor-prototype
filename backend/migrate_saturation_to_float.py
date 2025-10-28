#!/usr/bin/env python3
"""
PostgreSQL Migration: effect_saturation INTEGER → REAL (FLOAT)

PROBLEM:
- Frontend Slider sendet FLOAT-Werte (0.0 - 2.0 mit 0.1 Steps)
- Database Column ist INTEGER → rundet alle Werte!
- User stellt 1.5 ein → DB speichert 2 ❌

LÖSUNG:
- Column Type: INTEGER → REAL (PostgreSQL FLOAT)
- Konvertierung verlustfrei: 1 → 1.0, 2 → 2.0
- Alle 1931 Scenes behalten ihre Werte

TESTING:
✅ Local zuerst testen
✅ Dann auf Railway deployen
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
base_dir = Path(__file__).parent
load_dotenv(base_dir / '.env.local')
load_dotenv(base_dir / '.env')

def migrate_saturation_to_float():
    print("=" * 80)
    print("🔧 POSTGRESQL MIGRATION: effect_saturation INTEGER → REAL")
    print("=" * 80)

    db_url = os.getenv('DATABASE_URL')
    if not db_url or 'postgresql' not in db_url:
        print("❌ ERROR: No PostgreSQL DATABASE_URL found!")
        return False

    # Sanitize DB URL for display
    safe_url = db_url.split('@')[0].split(':')
    safe_url = f"{safe_url[0]}:***@" + db_url.split('@')[1]
    print(f"\n📍 Database: {safe_url}\n")

    engine = create_engine(db_url, echo=False, isolation_level="AUTOCOMMIT")

    try:
        with engine.connect() as conn:
            # 1. Show current state
            print("📊 BEFORE Migration:")
            result = conn.execute(text("""
                SELECT column_name, data_type, column_default
                FROM information_schema.columns
                WHERE table_name = 'scenes'
                AND column_name = 'effect_saturation'
            """))

            for row in result:
                col_name, data_type, default_val = row
                print(f"   {col_name:25} {data_type:30} default={default_val}")

            # Sample values BEFORE
            result = conn.execute(text("""
                SELECT id, effect_saturation
                FROM scenes
                ORDER BY updated_at DESC
                LIMIT 5
            """))
            print("\n   Sample values (5 most recent scenes):")
            for row in result:
                print(f"   Scene {row[0]}: saturation={row[1]}")

            # 2. ALTER COLUMN TYPE
            print(f"\n📝 Converting effect_saturation: INTEGER → REAL...")
            conn.execute(text("""
                ALTER TABLE scenes
                ALTER COLUMN effect_saturation TYPE REAL
                USING effect_saturation::real
            """))
            print("   ✅ Column type changed to REAL")

            # 3. Update default value
            conn.execute(text("""
                ALTER TABLE scenes
                ALTER COLUMN effect_saturation SET DEFAULT 1.0
            """))
            print("   ✅ Default changed: 1 → 1.0")

            # 4. Verification
            print("\n🔍 AFTER Migration:")
            result = conn.execute(text("""
                SELECT column_name, data_type, column_default
                FROM information_schema.columns
                WHERE table_name = 'scenes'
                AND column_name = 'effect_saturation'
            """))

            for row in result:
                col_name, data_type, default_val = row
                print(f"   {col_name:25} {data_type:30} default={default_val}")

            # Sample values AFTER
            result = conn.execute(text("""
                SELECT id, effect_saturation
                FROM scenes
                ORDER BY updated_at DESC
                LIMIT 5
            """))
            print("\n   Sample values (5 most recent scenes):")
            for row in result:
                print(f"   Scene {row[0]}: saturation={row[1]}")

            # Count total scenes
            result = conn.execute(text("SELECT COUNT(*) FROM scenes"))
            total = result.scalar()
            print(f"\n✅ Total scenes migrated: {total}")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 80)
    print("✅ MIGRATION SUCCESSFULLY COMPLETED!")
    print("=" * 80)
    print("\n💡 Next Steps:")
    print("   1. Update db_manager.py: Column(Integer) → Column(Float)")
    print("   2. Update video_effects.py: if saturation != 1 → if saturation != 1.0")
    print("   3. Git commit + push")
    print("   4. Test: Set saturation to 1.5 and verify it saves correctly\n")
    return True

if __name__ == '__main__':
    import sys
    success = migrate_saturation_to_float()
    sys.exit(0 if success else 1)
