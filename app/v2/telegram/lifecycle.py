"""FastAPI lifecycle for the shared v2 Telegram runtime."""

from __future__ import annotations

from app.v2.telegram.runtime_registry import shutdown_runtime


class TelegramRuntimeLifecycle:
    """Own the process-wide v2 runtime without eagerly connecting accounts."""

    async def startup(self) -> None:
        # Runtime/client creation remains lazy and happens on demand.
        return None

    async def shutdown(self) -> None:
        await shutdown_runtime()


def create_runtime_lifecycle() -> TelegramRuntimeLifecycle:
    return TelegramRuntimeLifecycle()
