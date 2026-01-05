"""Run database migrations for Task Organization Features.

Usage:
    cd backend
    python -m migrations.run_migration
"""

import os
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
import psycopg2

load_dotenv()


def get_database_url() -> str:
    """Get database URL from environment."""
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL environment variable is not set")

    # Convert to standard postgresql:// format for psycopg2
    # Remove asyncpg driver prefix if present
    if "postgresql+asyncpg://" in url:
        url = url.replace("postgresql+asyncpg://", "postgresql://", 1)
    elif url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    # Remove query params for psycopg2 (it uses sslmode in connect)
    if "?" in url:
        url = url.split("?")[0]

    return url


def run_migration():
    """Run the priority and tags migration."""
    migration_file = Path(__file__).parent / "001_add_priority_tags.sql"

    if not migration_file.exists():
        print(f"Error: Migration file not found: {migration_file}")
        sys.exit(1)

    sql = migration_file.read_text()

    db_url = get_database_url()
    print(f"Connecting to database...")

    try:
        conn = psycopg2.connect(db_url, sslmode="require")
        conn.autocommit = True

        with conn.cursor() as cur:
            print("Running migration: 001_add_priority_tags.sql")
            cur.execute(sql)
            print("Migration completed successfully!")

            # Verify columns exist
            cur.execute("""
                SELECT column_name, data_type, column_default
                FROM information_schema.columns
                WHERE table_name = 'tasks'
                AND column_name IN ('priority', 'tags')
                ORDER BY column_name;
            """)
            columns = cur.fetchall()
            print("\nVerification - New columns:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]} (default: {col[2]})")

        conn.close()
        print("\nMigration completed successfully!")

    except Exception as e:
        print(f"Error running migration: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_migration()
