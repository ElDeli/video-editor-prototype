#!/usr/bin/env python3
"""
Direct PostgreSQL Schema Fix - No Confirmation Required
Basierend auf SYSTEM_FLOW_ANALYSIS.md
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
base_dir = Path(__file__).parent
load_dotenv(base_dir / '.env.local')
load_dotenv(base_dir / '.env')

def execute_schema_fix():
    print("=" * 80)
    print("🔧 POSTGRESQL SCHEMA-FIX (DIRECT EXECUTION)")
    print("=" * 80)

    db_url = os.getenv('DATABASE_URL')
    if not db_url or 'postgresql' not in db_url:
        print("❌ ERROR: No PostgreSQL DATABASE_URL found!")
        return False

    safe_url = db_url.split('@')[0].split(':')
    safe_url = f"{safe_url[0]}:***@" + db_url.split('@')[1]
    print(f"\n📍 Database: {safe_url}\n")

    engine = create_engine(db_url, echo=False, isolation_level="AUTOCOMMIT")

    try:
        with engine.connect() as conn:
            # 1. effect_vignette: INTEGER → VARCHAR(50)
            print("📝 1/3: effect_vignette INTEGER → VARCHAR(50)...")
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
            print("   ✅ effect_vignette converted")

            # 2. effect_color_temp: INTEGER → VARCHAR(50)
            print("\n📝 2/3: effect_color_temp INTEGER → VARCHAR(50)...")
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
            print("   ✅ effect_color_temp converted")

            # 3. effect_saturation: 0 → 1 (FIXED: Use 1 instead of 50!)
            print("\n📝 3/3: effect_saturation: 0 → 1 (FFmpeg direct value)...")
            result = conn.execute(text("""
                UPDATE scenes
                SET effect_saturation = 1
                WHERE effect_saturation = 0
            """))
            print(f"   ✅ {result.rowcount} scenes updated (saturation: 0 → 1)")

            conn.execute(text("""
                ALTER TABLE scenes
                ALTER COLUMN effect_saturation SET DEFAULT 1
            """))
            print("   ✅ Default changed: 0 → 1")

            # Verification
            print("\n🔍 Verification...")
            result = conn.execute(text("""
                SELECT column_name, data_type, column_default
                FROM information_schema.columns
                WHERE table_name = 'scenes'
                AND column_name IN ('effect_vignette', 'effect_color_temp', 'effect_saturation')
                ORDER BY column_name
            """))

            for row in result:
                col_name, data_type, default_val = row
                print(f"   ✅ {col_name:25} {data_type:30} default={default_val}")

            # Sample values
            result = conn.execute(text("""
                SELECT effect_vignette, effect_color_temp, effect_saturation
                FROM scenes
                LIMIT 3
            """))

            print("\n📊 Sample Values (first 3 scenes):")
            for row in result:
                print(f"   vignette={row[0]}, color_temp={row[1]}, saturation={row[2]}")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 80)
    print("✅ SCHEMA-UPDATE SUCCESSFULLY COMPLETED!")
    print("=" * 80)
    return True

if __name__ == '__main__':
    import sys
    success = execute_schema_fix()
    sys.exit(0 if success else 1)
