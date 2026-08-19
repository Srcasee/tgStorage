"""Small environment-backed configuration for tgStorage v2."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    app_name: str = "tgStorage"
    version: str = "2.0"
    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./tgstorage.db")
    telegram_api_id: int | None = (
        int(os.environ["TELEGRAM_API_ID"])
        if os.getenv("TELEGRAM_API_ID")
        else None
    )
    telegram_api_hash: str | None = os.getenv("TELEGRAM_API_HASH")


settings = Settings()
