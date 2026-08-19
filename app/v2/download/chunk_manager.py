"""Chunk download planning primitives for v2.

Keeps range planning independent from Telegram/network backends.
Later implementations can attach workers that fetch ranges concurrently.
"""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class ChunkRange:
    start: int
    end: int

    @property
    def size(self) -> int:
        return max(0, self.end - self.start)


class ChunkManager:
    """Create deterministic byte ranges for a download task."""

    def split(self, file_size: int, chunk_size: int = 4 * 1024 * 1024) -> List[ChunkRange]:
        if file_size <= 0:
            return []

        chunks = []
        offset = 0
        while offset < file_size:
            end = min(offset + chunk_size, file_size)
            chunks.append(ChunkRange(start=offset, end=end))
            offset = end

        return chunks
