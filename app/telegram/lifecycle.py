"""FastAPI lifecycle for the shared Telegram runtime."""
from __future__ import annotations
from app.telegram.runtime_registry import shutdown_runtime

class TelegramRuntimeLifecycle:
    async def startup(self) -> None:
        return None
    async def shutdown(self) -> None:
        await shutdown_runtime()

def create_runtime_lifecycle() -> TelegramRuntimeLifecycle:
    return TelegramRuntimeLifecycle()
