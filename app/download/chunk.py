"""Chunk streaming abstractions for large resource downloads.

The implementation does not assume a specific storage backend. Telegram,
S3 or local storage backends can provide chunk readers through this layer.
"""

from typing import AsyncIterator, Protocol


class ChunkReader(Protocol):
    async def read_chunks(
        self,
        offset: int = 0,
        chunk_size: int = 256 * 1024,
    ) -> AsyncIterator[bytes]:
        ...


async def iter_chunks(
    reader: ChunkReader,
    offset: int = 0,
    chunk_size: int = 256 * 1024,
) -> AsyncIterator[bytes]:
    async for chunk in reader.read_chunks(
        offset=offset,
        chunk_size=chunk_size,
    ):
        yield chunk
