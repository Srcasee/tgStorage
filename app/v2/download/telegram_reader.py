from __future__ import annotations

from dataclasses import dataclass
from typing import AsyncIterator, Protocol


@dataclass
class TelegramChunk:
    offset: int
    data: bytes


class TelegramFileProvider(Protocol):
    async def read_chunk(
        self,
        chat_id: int,
        message_id: int,
        offset: int,
        limit: int,
    ) -> bytes:
        ...


class TelegramChunkReader:
    """Read Telegram resources as chunks.

    This layer intentionally does not create Telegram clients. Client lifecycle,
    account selection and proxy handling are delegated to the client pool and
    network plugin layers.
    """

    def __init__(self, provider: TelegramFileProvider):
        self.provider = provider

    async def stream(
        self,
        chat_id: int,
        message_id: int,
        start: int = 0,
        chunk_size: int = 256 * 1024,
        total_size: int | None = None,
    ) -> AsyncIterator[TelegramChunk]:
        offset = start

        while True:
            data = await self.provider.read_chunk(
                chat_id=chat_id,
                message_id=message_id,
                offset=offset,
                limit=chunk_size,
            )

            if not data:
                break

            yield TelegramChunk(offset=offset, data=data)
            offset += len(data)

            if total_size is not None and offset >= total_size:
                break
