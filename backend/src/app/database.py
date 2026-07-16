import socket
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from src.app.config import settings

import os

# Construct the SQLAlchemy database URL from configurations, supporting Heroku DATABASE_URL environment variable
database_url = os.getenv("DATABASE_URL")
if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    postgres_url = database_url
else:
    postgres_url = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

sqlite_url = "sqlite:///./auto_apply_local.db"

# Try connecting to PostgreSQL, fallback to SQLite if connection fails
fallback_to_sqlite = False
try:
    # Quick probe to see if Postgres is up
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

# If using SQLite fallback, ensure tables are created automatically on startup
if fallback_to_sqlite:
    # Import all models to bind metadata before create_all
    from src.app.models import User, Profile, UserSettings, JobFound, Application, EmailInteraction, CustomCoverLetter
    Base.metadata.create_all(bind=engine)

# DB dependency to yield session connections
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
