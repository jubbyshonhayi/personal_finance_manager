from pathlib import Path

from database.connection import pool


DATABASE_DIR = Path(__file__).parent
SCHEMA_FILE = DATABASE_DIR / "schema.sql"
SEED_FILE = DATABASE_DIR / "seed.sql"


def initialize_database():
    """
    Creates the database schema and required initial application data.
    """
    schema = SCHEMA_FILE.read_text(encoding="utf-8")
    seed = SEED_FILE.read_text(encoding="utf-8")

    with pool.connection() as connection:
        connection.execute(schema)
        connection.execute(seed)


if __name__ == "__main__":
    initialize_database()