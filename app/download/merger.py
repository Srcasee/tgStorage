"""Chunk merge primitives for v2 download streaming.

Keeps chunk ordering and assembly separate from storage backends.
"""

from dataclasses import dataclass
from typing import Dict, Iterable, Iterator


@dataclass(order=True)
class Chunk:
    start: int
    end: int
    data: bytes


class ChunkMerger:
    """Merge downloaded byte ranges in order."""

    def merge(self, chunks: Iterable[Chunk]) -> Iterator[bytes]:
        ordered = sorted(chunks, key=lambda item: item.start)
        for chunk in ordered:
            yield chunk.data

    def validate_range(self, start: int, end: int, size: int) -> bool:
        return 0 <= start <= end < size
