"""Telegram download backend boundary."""

from __future__ import annotations

from typing import AsyncIterator

from app.download.backend.telegram_runtime_adapter import TelegramRuntimeAdapter
from app.download.providers import DownloadBackend, ResourceLocation


class TelegramBackend(DownloadBackend):
    """Backend facade that delegates Telegram execution to runtime adapter."""

    def __init__(self, runtime_adapter: TelegramRuntimeAdapter):
        self.runtime_adapter = runtime_adapter

    async def stream(
        self,
        location: ResourceLocation,
        offset: int = 0,
        limit: int | None = None,
        chunk_size: int = 256 * 1024,
        account_id: int | None = None,
    ) -> AsyncIterator[bytes]:
        async for chunk in self.runtime_adapter.stream(
            location,
            offset=offset,
            limit=limit,
            chunk_size=chunk_size,
            account_id=account_id,
        ):
            yield chunk
