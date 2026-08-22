"""Process-local Telegram runtime registry."""
from __future__ import annotations

from app.core.config import settings
from app.network.registry import get_network_selector
from app.plugins.manager import PluginManager
from app.plugins.proxy import ProxyPlugin
from app.telegram.client_pool import TelegramClientPool
from app.telegram.provider import TelegramClientProvider
from app.telegram.runtime import TelegramClientConfig, TelegramClientRuntime

_runtime: TelegramClientRuntime | None = None
_provider: TelegramClientProvider | None = None
_pool: TelegramClientPool | None = None
_plugins: PluginManager | None = None


def get_plugin_manager() -> PluginManager:
    global _plugins
    if _plugins is None:
        _plugins = PluginManager()
        _plugins.register(ProxyPlugin())
    return _plugins


def get_runtime() -> TelegramClientRuntime:
    global _runtime
    if _runtime is None:
        if settings.telegram_api_id is None or not settings.telegram_api_hash:
            raise RuntimeError("Telegram API credentials are not configured")

        _runtime = TelegramClientRuntime(
            TelegramClientConfig(
                settings.telegram_api_id,
                settings.telegram_api_hash,
            ),
            get_network_selector(),
        )
    return _runtime


def get_provider() -> TelegramClientProvider:
    global _provider
    if _provider is None:
        _provider = TelegramClientProvider(get_runtime())
    return _provider


def get_pool() -> TelegramClientPool:
    global _pool
    if _pool is None:
        _pool = TelegramClientPool()
    return _pool


async def shutdown_runtime() -> None:
    global _runtime, _provider, _pool, _plugins
    if _runtime is not None:
        await _runtime.disconnect_all()
    if _plugins is not None:
        await _plugins.shutdown()
    _provider = None
    _runtime = None
    _pool = None
    _plugins = None
