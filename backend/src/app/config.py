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
    
    # OpenAI & Embeddings Configurations
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # Search Agent Configurations
    ADZUNA_APP_ID: Optional[str] = None
    ADZUNA_APP_KEY: Optional[str] = None
    JOOBLE_API_KEY: Optional[str] = None
    TRACKED_COMPANIES_GREENHOUSE: list[str] = ["stripe", "vercel", "openai", "cloudflare"]
    TRACKED_COMPANIES_LEVER: list[str] = ["figma", "vercel", "openai", "palantir"]
    SEARCH_INTERVAL_HOURS: int = 6
    
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
