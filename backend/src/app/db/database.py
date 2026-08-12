import socket
import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from src.app.core.config import settings

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

engine = None
fallback_to_sqlite = False

# Try connecting to PostgreSQL
if database_url or (settings.POSTGRES_SERVER and settings.POSTGRES_SERVER != "localhost"):
    try:
        connect_args = {}
        # Heroku Postgres requires sslmode=require for secure cloud connections
        if "postgresql" in postgres_url and not any(host in postgres_url for host in ["localhost", "127.0.0.1", "@postgres:", "@auto_apply_postgres:"]):
            connect_args = {"sslmode": "require"}
            
        test_engine = create_engine(postgres_url, pool_pre_ping=True, connect_args=connect_args)
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine = test_engine
        SQLALCHEMY_DATABASE_URL = postgres_url
        logger.info("Successfully connected to PostgreSQL database!")
    except Exception as e:
        logger.warning(f"PostgreSQL connection test failed ({e}). Falling back to local SQLite database.")

if not engine:
    SQLALCHEMY_DATABASE_URL = sqlite_url
    engine = create_engine(sqlite_url, pool_pre_ping=True, connect_args={"check_same_thread": False})
    fallback_to_sqlite = True

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def sync_sqlite_schema(db_engine):
    """
    Dynamically inspects ALL SQLAlchemy models and automatically adds ANY missing column
    to existing SQLite tables so OperationalError 'no such column' can NEVER happen.
    """
    try:
        from src.app.db.models import User, Profile, UserSettings, JobFound, Application, EmailInteraction, CustomCoverLetter
        with db_engine.connect() as conn:
            for table_name, table in Base.metadata.tables.items():
                cursor = conn.execute(text(f"PRAGMA table_info({table_name})"))
                existing_cols = {row[1] for row in cursor.fetchall()}
                if not existing_cols:
                    continue
                
                for col in table.columns:
                    if col.name not in existing_cols:
                        col_type = str(col.type).upper()
                        if "JSON" in col_type:
                            sql_type = "JSON"
                        elif "INT" in col_type:
                            sql_type = "INTEGER"
                        elif "BOOL" in col_type:
                            sql_type = "BOOLEAN"
                        elif "DATETIME" in col_type:
                            sql_type = "DATETIME"
                        else:
                            sql_type = "VARCHAR"
                        
                        alter_query = f"ALTER TABLE {table_name} ADD COLUMN {col.name} {sql_type}"
                        try:
                            conn.execute(text(alter_query))
                            conn.commit()
                            logger.info(f"Auto-migrated SQLite column: {table_name}.{col.name}")
                        except Exception as ex:
                            logger.warning(f"Could not alter {table_name}.{col.name}: {ex}")
    except Exception as e:
        logger.warning(f"SQLite dynamic schema sync warning: {e}")

from src.app.db import models
Base.metadata.create_all(bind=engine)

# If using SQLite fallback, ensure tables are created & synced automatically on startup
if fallback_to_sqlite:
    sync_sqlite_schema(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
