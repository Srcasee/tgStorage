from __future__ import annotations

from typing import AsyncIterator, Protocol


class TelegramStreamBackend(Protocol):
    """Telegram download backend abstraction.

    The concrete Telegram client integration is injected later so download
    routing can stay independent from Telethon and network plugins.
    """

    async def stream(
        self,
        resource_id: int,
        chunk_size: int = 256 * 1024,
    ) -> AsyncIterator[bytes]:
        raise NotImplementedError


class DefaultTelegramStreamBackend:
    """Base Telegram streaming backend placeholder.

    This keeps the HTTP download layer independent from Telegram session
    management. The implementation will bind to the existing Telegram client
    pool in the next step.
    """

    async def stream(
        self,
        resource_id: int,
        chunk_size: int = 256 * 1024,
    ) -> AsyncIterator[bytes]:
        raise NotImplementedError("Telegram backend is not configured")
