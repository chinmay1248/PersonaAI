from functools import lru_cache

from pydantic import AliasChoices, Field
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
    llm_provider: str = Field(default="ollama", validation_alias=AliasChoices("LLM_PROVIDER"))
    llm_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("LLM_API_KEY", "GEMINI_API_KEY", "OPENAI_API_KEY"),
    )
    enable_llm: bool = Field(default=False, validation_alias=AliasChoices("ENABLE_LLM", "ENABLE_OPENAI"))
    llm_base_url: str | None = Field(default=None, validation_alias=AliasChoices("LLM_BASE_URL"))
    llm_chat_model: str | None = Field(default=None, validation_alias=AliasChoices("LLM_CHAT_MODEL"))
    llm_fast_model: str | None = Field(default=None, validation_alias=AliasChoices("LLM_FAST_MODEL"))
    llm_embedding_model: str | None = Field(
        default=None,
        validation_alias=AliasChoices("LLM_EMBEDDING_MODEL"),
    )
    pinecone_api_key: str | None = Field(default=None, alias="PINECONE_API_KEY")
    pinecone_environment: str | None = Field(default=None, alias="PINECONE_ENVIRONMENT")

    @property
    def normalized_llm_provider(self) -> str:
        return (self.llm_provider or "ollama").strip().lower()

    @property
    def llm_enabled(self) -> bool:
        if not self.enable_llm:
            return False
        if self.normalized_llm_provider in {"openai", "gemini"}:
            return bool(self.llm_api_key)
        return True

    @property
    def resolved_llm_base_url(self) -> str | None:
        if self.llm_base_url:
            return self.llm_base_url.rstrip("/")
        if self.normalized_llm_provider == "ollama":
            return "http://localhost:11434/v1"
        if self.normalized_llm_provider == "gemini":
            return "https://generativelanguage.googleapis.com/v1beta/openai"
        return None

    @property
    def resolved_chat_model(self) -> str:
        if self.llm_chat_model:
            return self.llm_chat_model
        if self.normalized_llm_provider == "gemini":
            return "gemini-2.5-flash"
        if self.normalized_llm_provider == "openai":
            return "gpt-4o"
        return "llama3.2:3b"

    @property
    def resolved_fast_model(self) -> str:
        if self.llm_fast_model:
            return self.llm_fast_model
        if self.normalized_llm_provider == "gemini":
            return "gemini-2.5-flash-lite"
        if self.normalized_llm_provider == "openai":
            return "gpt-4o-mini"
        return self.resolved_chat_model

    @property
    def resolved_embedding_model(self) -> str:
        if self.llm_embedding_model:
            return self.llm_embedding_model
        if self.normalized_llm_provider == "gemini":
            return "gemini-embedding-001"
        if self.normalized_llm_provider == "openai":
            return "text-embedding-3-small"
        return "nomic-embed-text"

    @property
    def openai_enabled(self) -> bool:
        return self.llm_enabled


@lru_cache
def get_settings() -> Settings:
    return Settings()
