"""FastAPI lifecycle for the shared Telegram runtime."""
from __future__ import annotations

from app.network.loader import load_network_plugins
from app.network.selector import NetworkSelector
from app.telegram.runtime_registry import shutdown_runtime


class TelegramRuntimeLifecycle:
    def __init__(self) -> None:
        self.network_selector = NetworkSelector()

    async def startup(self) -> None:
        load_network_plugins(self.network_selector)

    async def shutdown(self) -> None:
        await shutdown_runtime()


def create_runtime_lifecycle() -> TelegramRuntimeLifecycle:
    return TelegramRuntimeLifecycle()
