import os

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables from .env when present.
load_dotenv()

PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "postgres")
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_DATABASE = os.getenv("PG_DATABASE", "pipeline_db")


def get_connection_string(db_name: str | None = None) -> str:
    """Return a PostgreSQL connection string for the chosen database."""
    database = db_name if db_name else PG_DATABASE
    return f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{database}"


def get_engine(db_name: str | None = None):
    """Return a SQLAlchemy engine for the chosen database."""
    return create_engine(get_connection_string(db_name))


def create_database_if_not_exists() -> None:
    """Create the target PostgreSQL database when missing."""
    try:
        admin_engine = get_engine("postgres")
        with admin_engine.connect() as connection:
            result = connection.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname='{PG_DATABASE}'")
            )
            exists = result.scalar() == 1

        if exists:
            print(f"Database '{PG_DATABASE}' already exists.")
            return

        print(f"Database '{PG_DATABASE}' not found. Creating...")
        autocommit_engine = create_engine(
            get_connection_string("postgres"), isolation_level="AUTOCOMMIT"
        )
        with autocommit_engine.connect() as connection:
            connection.execute(text(f'CREATE DATABASE "{PG_DATABASE}"'))
        autocommit_engine.dispose()
        print(f"Database '{PG_DATABASE}' created successfully.")

    except Exception as exc:  # noqa: BLE001
        print(f"Error while ensuring database exists: {exc}")
        raise
