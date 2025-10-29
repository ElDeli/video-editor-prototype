"""
Migration: Add image_path column to scenes table
"""
from database.db_manager import DatabaseManager
from sqlalchemy import text

def run_migration():
    print("🔄 Running migration: Add image_path to scenes table...")

    db = DatabaseManager()
    session = db.Session()

    try:
        # Check if column exists
        result = session.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name='scenes' AND column_name='image_path'"
        ))
        exists = result.fetchone()

        if exists:
            print("✅ image_path column already exists - migration not needed")
            return True

        # Add the column
        print("➕ Adding image_path column to scenes table...")
        session.execute(text("ALTER TABLE scenes ADD COLUMN image_path TEXT"))
        session.commit()
        print("✅ Migration completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        session.rollback()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    success = run_migration()
    exit(0 if success else 1)
