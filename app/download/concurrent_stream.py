from __future__ import annotations

from collections.abc import AsyncIterator, Iterable

from .chunk import ChunkRange
from .chunk_manager import ChunkManager
from .chunk_merger import ChunkMerger
from .chunk_scheduler import ChunkResult, ChunkScheduler
from .chunk_worker import ChunkWorker


class ConcurrentChunkStream:
    """Build an ordered byte stream from concurrently executed chunks."""

    def __init__(
        self,
        scheduler: ChunkScheduler,
        merger: ChunkMerger,
        chunk_manager: ChunkManager,
    ) -> None:
        self.scheduler = scheduler
        self.merger = merger
        self.chunk_manager = chunk_manager

    async def stream(
        self,
        worker: ChunkWorker,
        file_size: int,
        chunk_size: int,
    ) -> AsyncIterator[bytes]:
        chunks: Iterable[ChunkRange] = self.chunk_manager.split(
            file_size=file_size,
            chunk_size=chunk_size,
        )

        results: list[ChunkResult] = await self.scheduler.execute(
            worker,
            chunks,
        )

        async for data in self.merger.merge(results):
            yield data
