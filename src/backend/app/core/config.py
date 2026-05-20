from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = Field(
        default="postgresql+psycopg2://aero:aero@localhost:5432/aero",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    opensky_base_url: str = Field(
        default="https://opensky-network.org/api",
        alias="OPENSKY_BASE_URL",
    )
    opensky_username: str | None = Field(default=None, alias="OPENSKY_USERNAME")
    opensky_password: str | None = Field(default=None, alias="OPENSKY_PASSWORD")
    opensky_poll_seconds: int = Field(default=10, alias="OPENSKY_POLL_SECONDS")

    redis_updates_channel: str = Field(
        default="aircraft.updates",
        alias="REDIS_UPDATES_CHANNEL",
    )

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
