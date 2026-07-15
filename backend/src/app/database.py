from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from src.app.config import settings

# Construct the SQLAlchemy database URL from configurations
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True  # Enables database connection health checks on query
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# DB dependency to yield session connections
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
