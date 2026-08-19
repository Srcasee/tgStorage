from __future__ import annotations

from typing import AsyncIterator

from .resource_resolver import ResourceResolver
from .telegram_reader import TelegramChunkReader


class TelegramStreamBackend:
    """Stream indexed Telegram resources through an injected reader."""

    def __init__(self, resolver: ResourceResolver, reader: TelegramChunkReader):
        self.resolver = resolver
        self.reader = reader

    async def stream(
        self,
        resource_id: int,
        start: int = 0,
        limit: int | None = None,
        chunk_size: int = 256 * 1024,
    ) -> AsyncIterator[bytes]:
        location = await self.resolver.resolve_telegram(resource_id)
        total_size = location.size or None
        if total_size is not None and start >= total_size:
            return

        remaining = limit
        async for chunk in self.reader.stream(
            chat_id=location.chat_id,
            message_id=location.message_id,
            start=start,
            chunk_size=chunk_size,
            total_size=total_size,
            account_id=location.account_id,
        ):
            data = chunk.data
            if remaining is not None:
                if remaining <= 0:
                    break
                if len(data) > remaining:
                    data = data[:remaining]
                remaining -= len(data)
            if data:
                yield data
            if remaining == 0:
                break
