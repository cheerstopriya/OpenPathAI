"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated settings for the API process.

    The prefix prevents accidental collisions with unrelated machine variables.
    Real secrets will be supplied through the environment, never committed files.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="OPENPATH_",
        extra="ignore",
    )

    environment: str = "development"
    log_level: str = "INFO"
    api_title: str = "OpenPath AI API"
    api_version: str = "0.1.0"


@lru_cache
def get_settings() -> Settings:
    """Create settings once per process instead of parsing the environment per request."""

    return Settings()

