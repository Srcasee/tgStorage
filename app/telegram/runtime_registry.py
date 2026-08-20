"""Process-local Telegram runtime registry."""
from __future__ import annotations

from app.core.config import settings
from app.telegram.client_pool import TelegramClientPool
from app.telegram.runtime import TelegramClientConfig, TelegramClientRuntime

_runtime: TelegramClientRuntime | None = None
_pool: TelegramClientPool | None = None


def get_runtime() -> TelegramClientRuntime:
    global _runtime
    if _runtime is None:
        if settings.telegram_api_id is None or not settings.telegram_api_hash:
            raise RuntimeError("Telegram API credentials are not configured")

        _runtime = TelegramClientRuntime(
            TelegramClientConfig(
                settings.telegram_api_id,
                settings.telegram_api_hash,
                settings.proxy,
            )
        )
    return _runtime


def get_pool() -> TelegramClientPool:
    global _pool
    if _pool is None:
        _pool = TelegramClientPool()
    return _pool


async def shutdown_runtime() -> None:
    global _runtime, _pool
    if _runtime is not None:
        await _runtime.disconnect_all()
    _runtime = None
    _pool = None
