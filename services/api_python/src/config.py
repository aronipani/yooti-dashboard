"""
Application configuration — loaded from environment variables.
Never hardcode values here. Add all new config to .env.example.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    environment: str = "development"
    debug: bool = False
    port: int = 8000
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Database
    database_url: str = "postgresql+asyncpg://app:app@localhost:5432/appdb"
    # Redis
    redis_url: str = "redis://localhost:6379"
    # LLM
    anthropic_api_key: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
