"""tgStorage v2 core configuration.

Keeps deployment configuration lightweight while allowing
SQLite/PostgreSQL switching through environment variables.
"""

from dataclasses import dataclass
import os


@dataclass
class Settings:
    app_name: str = "tgStorage"
    version: str = "2.0"
    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./tgstorage.db",
    )


settings = Settings()
