from functools import lru_cache
import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "PersonaAI API"
    app_env: str = Field(default="development", alias="APP_ENV")

    # Auto-resolves to False in production (Railway sets APP_ENV=production)
    @property
    def debug(self) -> bool:
        return self.app_env != "production"

    api_prefix: str = "/v1"

    # Railway automatically injects DATABASE_URL pointing to its PostgreSQL instance.
    # Falls back to local SQLite for development.
    database_url: str = Field(default="sqlite:///./personaai.db", alias="DATABASE_URL")

    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    jwt_secret_key: str = Field(default="dev-jwt-secret-key-change-in-production", alias="JWT_SECRET_KEY")
    encryption_key: str = Field(default="bEKZ79oM5rtwR5gBcTeQWzUWRTyAPL55iT0fct_g024=", alias="ENCRYPTION_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=30, alias="REFRESH_TOKEN_EXPIRE_DAYS")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    pinecone_api_key: str | None = Field(default=None, alias="PINECONE_API_KEY")
    pinecone_environment: str | None = Field(default=None, alias="PINECONE_ENVIRONMENT")


@lru_cache
def get_settings() -> Settings:
    return Settings()
