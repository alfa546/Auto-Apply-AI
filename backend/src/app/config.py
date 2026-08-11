# Configuration loader
import logging
import os
import json
import warnings
from typing import Optional, Annotated, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict, NoDecode

logger = logging.getLogger(__name__)


def _normalize_str_list(value):
    """
    Coerce a raw env value (or already-decoded list/tuple) into a clean list of strings.

    Accepts:
      - JSON arrays:   '["http://a.com", "http://b.com"]'
      - Comma separated: 'http://a.com,http://b.com'
      - Single value:    'http://a.com'
      - Python list/tuple (e.g. via constructor)
    """
    if value is None:
        return []
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []
        if stripped.startswith("["):
            try:
                decoded = json.loads(stripped)
                if isinstance(decoded, list):
                    return [str(item).strip() for item in decoded if str(item).strip()]
            except (ValueError, json.JSONDecodeError):
                pass
        return [item.strip() for item in stripped.split(",") if item.strip()]
    if isinstance(value, (list, tuple, set)):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value)]


class Settings(BaseSettings):
    PROJECT_NAME: str = "Auto Apply AI"
    API_V1_STR: str = "/api/v1"

    # Frontend / integration
    FRONTEND_BASE_URL: str = "http://localhost:3000"
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    # CORS & hosts - NoDecode lets us accept plain comma-separated strings
    # from .env AND JSON arrays without crashing the app at startup.
    CORS_ORIGINS: Annotated[list[str], NoDecode] = ["http://localhost:3000"]
    ALLOWED_HOSTS: Annotated[list[str], NoDecode] = ["*"]  # lock down per deployment in prod
    # Database Configurations
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "auto_apply_db"
    POSTGRES_PORT: str = "5432"
    
    # Redis Configurations
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    

    # Firebase Setup
    FIREBASE_PROJECT_ID: Optional[str] = None
    FIREBASE_STORAGE_BUCKET: Optional[str] = None
    
    # OpenAI Configurations
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # Gemini Configurations
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"
    
    # Search Agent Configurations
    ADZUNA_APP_ID: Optional[str] = None
    ADZUNA_APP_KEY: Optional[str] = None
    JOOBLE_API_KEY: Optional[str] = None
    TRACKED_COMPANIES_GREENHOUSE: Annotated[list[str], NoDecode] = ["vercel", "openai", "cloudflare"]
    TRACKED_COMPANIES_LEVER: Annotated[list[str], NoDecode] = ["figma", "vercel", "openai"]
    SEARCH_INTERVAL_HOURS: int = 6
    MATCHING_THRESHOLD: float = 0.8
    PLAYWRIGHT_HEADLESS: bool = True
    PLAYWRIGHT_TIMEOUT: int = 30000
    
    # Email & Gmail OAuth Configurations
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/gmail/callback"
    EMAIL_IMAP_SERVER: Optional[str] = None
    EMAIL_SMTP_SERVER: str = "smtp.gmail.com"
    EMAIL_SMTP_PORT: int = 587
    EMAIL_ADDRESS: Optional[str] = None
    EMAIL_PASSWORD: Optional[str] = None
    EMAIL_CHECK_INTERVAL_MINUTES: int = 15
    
    # Notification Agent Configurations
    DISCORD_WEBHOOK_URL: Optional[str] = None
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None
    
    # Security Setup
    SECRET_KEY: str = "supersecretdevelopmentkeychangeinprod"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("CORS_ORIGINS", "ALLOWED_HOSTS", "TRACKED_COMPANIES_GREENHOUSE", "TRACKED_COMPANIES_LEVER", mode="before")
    @classmethod
    def _coerce_list_fields(cls, v: Union[str, list, tuple, None]):
        return _normalize_str_list(v)

    @field_validator("SECRET_KEY", mode="after")
    @classmethod
    def _validate_secret_key(cls, v: str) -> str:
        if v in (
            "supersecretdevelopmentkeychangeinprod",
            "replace_this_with_a_properly_generated_secure_secret_key_in_production",
        ):
            warnings.warn(
                "SECRET_KEY is still set to a known insecure development default. "
                "Generate a strong random key (e.g. `python -c \"import secrets; print(secrets.token_hex(32))\"`) "
                "and set it in your .env before deploying.",
                stacklevel=2,
            )
        if len(v) < 32:
            warnings.warn(
                f"SECRET_KEY is only {len(v)} characters long. Use at least 32 characters in production.",
                stacklevel=2,
            )
        return v

    @field_validator("MAX_UPLOAD_SIZE_MB")
    @classmethod
    def _validate_upload_size(cls, v: int) -> int:
        return max(1, min(v, 100))


settings = Settings()
