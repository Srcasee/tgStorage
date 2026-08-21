from __future__ import annotations

from typing import AsyncIterator, Iterable

from .chunk_scheduler import ChunkResult


class ChunkMerger:
    """Merge completed chunks into an ordered byte stream.

    Chunk execution may complete out of order when using concurrent workers.
    This merger restores byte order using the original chunk offsets.
    """

    async def merge(
        self,
        results: Iterable[ChunkResult],
    ) -> AsyncIterator[bytes]:
        ordered = sorted(results, key=lambda item: item.chunk.start)

        for result in ordered:
            if result.data:
                yield result.data
