# Configuration loader
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Auto Apply AI"
    API_V1_STR: str = "/api/v1"
    
    # Database Configurations
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "auto_apply_db"
    POSTGRES_PORT: str = "5432"
    
    # Redis Configurations
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # Vector Database Configurations
    CHROMADB_HOST: str = "localhost"
    CHROMADB_PORT: int = 8000
    
    # Firebase Setup
    FIREBASE_PROJECT_ID: Optional[str] = None
    FIREBASE_STORAGE_BUCKET: Optional[str] = None
    
    # Security Setup
    SECRET_KEY: str = "supersecretdevelopmentkeychangeinprod"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 1 week
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
