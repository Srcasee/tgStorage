from __future__ import annotations

from dataclasses import dataclass
from typing import AsyncIterator

from .providers import TelegramFileProvider


@dataclass
class TelegramChunk:
    offset: int
    data: bytes


class TelegramChunkReader:
    """Read Telegram media through the injected storage provider."""

    def __init__(self, provider: TelegramFileProvider):
        self.provider = provider

    async def stream(
        self,
        chat_id: int,
        message_id: int,
        start: int = 0,
        chunk_size: int = 256 * 1024,
        total_size: int | None = None,
        account_id: int | None = None,
    ) -> AsyncIterator[TelegramChunk]:
        offset = start
        remaining = None if total_size is None else max(total_size - start, 0)

        async for data in self.provider.stream_message(
            chat_id=chat_id,
            message_id=message_id,
            offset=start,
            limit=remaining,
            chunk_size=chunk_size,
            account_id=account_id,
        ):
            if not data:
                break
            yield TelegramChunk(offset=offset, data=data)
            offset += len(data)
