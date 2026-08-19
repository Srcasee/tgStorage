"""Small environment-backed configuration for tgStorage."""

from dataclasses import dataclass
import os


def _env_first(*names: str) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return None


@dataclass(frozen=True)
class Settings:
    app_name: str = "tgStorage"
    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./tgstorage.db")
    telegram_api_id: int | None = None
    telegram_api_hash: str | None = None

    def __post_init__(self) -> None:
        api_id = _env_first("TELEGRAM_API_ID", "TG_API_ID")
        object.__setattr__(self, "telegram_api_id", int(api_id) if api_id else None)
        object.__setattr__(self, "telegram_api_hash", _env_first("TELEGRAM_API_HASH", "TG_API_HASH"))


settings = Settings()
