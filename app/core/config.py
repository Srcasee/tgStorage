"""Environment-backed configuration for tgStorage."""

from dataclasses import dataclass
import os

from dotenv import load_dotenv


# Load local development configuration without overriding real environment values.
load_dotenv(override=False)


def _env_first(*names: str) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return None


def _env_bool(*names: str, default: bool = False) -> bool:
    value = _env_first(*names)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class ProxySettings:
    enabled: bool = False
    host: str | None = None
    port: int | None = None
    proxy_type: str | None = None


@dataclass(frozen=True)
class Settings:
    app_name: str = "tgStorage"
    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./tgstorage.db")
    telegram_api_id: int | None = None
    telegram_api_hash: str | None = None
    proxy: ProxySettings = ProxySettings()

    def __post_init__(self) -> None:
        api_id = _env_first("TG_API_ID", "TELEGRAM_API_ID")
        object.__setattr__(self, "telegram_api_id", int(api_id) if api_id else None)
        object.__setattr__(self, "telegram_api_hash", _env_first("TG_API_HASH", "TELEGRAM_API_HASH"))

        proxy = ProxySettings(
            enabled=_env_bool("ENABLE_PROXY"),
            host=_env_first("PROXY_HOST"),
            port=int(_env_first("PROXY_PORT") or 0) or None,
            proxy_type=_env_first("PROXY_TYPE"),
        )
        object.__setattr__(self, "proxy", proxy)


settings = Settings()
