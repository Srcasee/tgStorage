from __future__ import annotations

from .chunk_manager import ChunkRange
from .chunk_scheduler import ChunkWorker
from .telegram_reader import TelegramChunkReader


class TelegramChunkWorker(ChunkWorker):
    """Adapt TelegramChunkReader into the generic ChunkWorker interface."""

    def __init__(
        self,
        reader: TelegramChunkReader,
        chat_id: int,
        message_id: int,
        account_id: int | None = None,
        chunk_size: int = 256 * 1024,
    ) -> None:
        self.reader = reader
        self.chat_id = chat_id
        self.message_id = message_id
        self.account_id = account_id
        self.chunk_size = chunk_size

    async def fetch(self, chunk: ChunkRange) -> bytes:
        data = bytearray()

        async for item in self.reader.stream(
            chat_id=self.chat_id,
            message_id=self.message_id,
            start=chunk.start,
            chunk_size=self.chunk_size,
            total_size=chunk.size,
            account_id=self.account_id,
        ):
            data.extend(item.data)

        return bytes(data)
