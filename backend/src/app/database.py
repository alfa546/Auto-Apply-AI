import socket
import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from src.app.config import settings

logger = logging.getLogger(__name__)

# Construct the SQLAlchemy database URL from configurations
database_url = os.getenv("DATABASE_URL")
if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    postgres_url = database_url
else:
    postgres_url = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

sqlite_url = "sqlite:///./auto_apply_local.db"

fallback_to_sqlite = False
try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)
        s.connect((settings.POSTGRES_SERVER, int(settings.POSTGRES_PORT)))
    SQLALCHEMY_DATABASE_URL = postgres_url
    connect_args = {}
except Exception:
    print("PostgreSQL is offline. Falling back to local SQLite database: auto_apply_local.db")
    SQLALCHEMY_DATABASE_URL = sqlite_url
    connect_args = {"check_same_thread": False}
    fallback_to_sqlite = True

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def sync_sqlite_schema(db_engine):
    """
    Auto-inspects SQLite tables and dynamically adds missing columns
    so SQLite local DB never fails with 'no such column' OperationalErrors.
    """
    try:
        with db_engine.connect() as conn:
            # 1. jobs_found table
            cursor = conn.execute(text("PRAGMA table_info(jobs_found)"))
            cols = [row[1] for row in cursor.fetchall()]
            if cols:
                if "country" not in cols:
                    conn.execute(text("ALTER TABLE jobs_found ADD COLUMN country VARCHAR"))
                if "company_email" not in cols:
                    conn.execute(text("ALTER TABLE jobs_found ADD COLUMN company_email VARCHAR"))
                if "opportunity_type" not in cols:
                    conn.execute(text("ALTER TABLE jobs_found ADD COLUMN opportunity_type VARCHAR DEFAULT 'job'"))
                if "match_score" not in cols:
                    conn.execute(text("ALTER TABLE jobs_found ADD COLUMN match_score INTEGER DEFAULT 85"))
                conn.commit()

            # 2. applications table
            cursor = conn.execute(text("PRAGMA table_info(applications)"))
            cols = [row[1] for row in cursor.fetchall()]
            if cols:
                if "company_email" not in cols:
                    conn.execute(text("ALTER TABLE applications ADD COLUMN company_email VARCHAR"))
                if "opportunity_type" not in cols:
                    conn.execute(text("ALTER TABLE applications ADD COLUMN opportunity_type VARCHAR DEFAULT 'job'"))
                if "notes" not in cols:
                    conn.execute(text("ALTER TABLE applications ADD COLUMN notes VARCHAR"))
                conn.commit()

            # 3. user_settings table
            cursor = conn.execute(text("PRAGMA table_info(user_settings)"))
            cols = [row[1] for row in cursor.fetchall()]
            if cols:
                if "target_roles" not in cols:
                    conn.execute(text("ALTER TABLE user_settings ADD COLUMN target_roles JSON"))
                if "preferred_countries" not in cols:
                    conn.execute(text("ALTER TABLE user_settings ADD COLUMN preferred_countries JSON"))
                if "llm_provider" not in cols:
                    conn.execute(text("ALTER TABLE user_settings ADD COLUMN llm_provider VARCHAR DEFAULT 'openai'"))
                if "llm_model" not in cols:
                    conn.execute(text("ALTER TABLE user_settings ADD COLUMN llm_model VARCHAR DEFAULT 'gpt-4o'"))
                if "custom_api_base" not in cols:
                    conn.execute(text("ALTER TABLE user_settings ADD COLUMN custom_api_base VARCHAR"))
                conn.commit()
    except Exception as e:
        logger.warning(f"SQLite schema sync warning: {e}")

# If using SQLite fallback, ensure tables are created & synced automatically on startup
if fallback_to_sqlite:
    from src.app.models import User, Profile, UserSettings, JobFound, Application, EmailInteraction, CustomCoverLetter
    Base.metadata.create_all(bind=engine)
    sync_sqlite_schema(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
