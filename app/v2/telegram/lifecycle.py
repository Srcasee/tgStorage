"""FastAPI-friendly lifecycle for the v2 Telegram runtime."""

from __future__ import annotations

from app.v2.telegram.runtime import TelegramClientRuntime


class TelegramRuntimeLifecycle:
    """Owns startup/shutdown without changing the legacy scanner bootstrap."""

    def __init__(self, runtime: TelegramClientRuntime) -> None:
        self.runtime = runtime

    async def startup(self) -> None:
        """Runtime is lazy: clients connect only when a download/scanner needs one."""
        return None

    async def shutdown(self) -> None:
        await self.runtime.disconnect_all()
