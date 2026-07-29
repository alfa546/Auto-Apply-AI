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
    Dynamically inspects ALL SQLAlchemy models and automatically adds ANY missing column
    to existing SQLite tables so OperationalError 'no such column' can NEVER happen.
    """
    try:
        from src.app.models import User, Profile, UserSettings, JobFound, Application, EmailInteraction, CustomCoverLetter
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
                            print(f"Auto-migrated SQLite column: {table_name}.{col.name}")
                        except Exception as ex:
                            logger.warning(f"Could not alter {table_name}.{col.name}: {ex}")
    except Exception as e:
        logger.warning(f"SQLite dynamic schema sync warning: {e}")

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
