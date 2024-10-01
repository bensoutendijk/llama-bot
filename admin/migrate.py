import os
import sys
import psycopg2
import time
import logging
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Update the MIGRATIONS_DIR path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
MIGRATIONS_DIR = os.path.join("/db/migrations")


def wait_for_database(max_retries=30, delay=2):
    retries = 0
    while retries < max_retries:
        try:
            logger.info(
                f"Attempting to connect to database (attempt {retries + 1}/{max_retries})"
            )
            conn = psycopg2.connect(
                host=os.getenv("POSTGRES_HOST"),
                database=os.getenv("POSTGRES_DB"),
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
            )
            conn.close()
            logger.info("Database is available.")
            return
        except psycopg2.OperationalError as e:
            logger.error(f"Database connection error: {e}")
            retries += 1
            logger.info(f"Waiting for {delay} seconds before next attempt...")
            time.sleep(delay)

    logger.critical("Unable to connect to the database after multiple attempts")
    raise Exception("Unable to connect to the database after multiple attempts")


def get_applied_migrations(cur):
    logger.info("Checking for applied migrations")
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS migration_history (
        id SERIAL PRIMARY KEY,
        migration_id VARCHAR(50) NOT NULL,
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    )
    cur.execute("SELECT migration_id FROM migration_history ORDER BY id")
    applied = {row[0] for row in cur.fetchall()}
    logger.info(f"Found {len(applied)} applied migrations")
    return applied


def apply_migration(cur, migration_id):
    logger.info(f"Applying migration: {migration_id}")
    with open(os.path.join(MIGRATIONS_DIR, migration_id), "r") as f:
        sql = f.read()
    try:
        cur.execute(sql)
        cur.execute(
            "INSERT INTO migration_history (migration_id) VALUES (%s)", (migration_id,)
        )
        logger.info(f"Successfully applied migration: {migration_id}")
    except Exception as e:
        logger.error(f"Error applying migration {migration_id}: {e}")
        raise


def run_migrations():
    logger.info("Starting migration process")
    wait_for_database()

    try:
        logger.info("Connecting to database for migrations")
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            database=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
        )

        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        applied_migrations = get_applied_migrations(cur)

        if not os.path.exists(MIGRATIONS_DIR):
            logger.warning(f"Migrations directory not found: {MIGRATIONS_DIR}")
            return

        migration_files = sorted(os.listdir(MIGRATIONS_DIR))

        if not migration_files:
            logger.info("No migration files found.")
            return

        for migration_file in migration_files:
            if (
                migration_file.endswith(".sql")
                and migration_file not in applied_migrations
            ):
                apply_migration(cur, migration_file)

        logger.info("Migration process completed successfully")
    except Exception as e:
        logger.error(f"Error during migration process: {e}")
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    try:
        run_migrations()
    except Exception as e:
        logger.critical(f"Migration failed: {e}")
        sys.exit(1)
