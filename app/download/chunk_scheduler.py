from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Iterable, Protocol

from .chunk_manager import ChunkRange


class ChunkWorker(Protocol):
    async def fetch(self, chunk: ChunkRange) -> bytes:
        ...


@dataclass
class ChunkResult:
    chunk: ChunkRange
    data: bytes


class ChunkScheduler:
    """Coordinates chunk workers.

    Scheduling is independent from Telegram and network implementations.
    """

    def __init__(self, worker: ChunkWorker, max_concurrency: int = 4) -> None:
        self.worker = worker
        self.max_concurrency = max(1, max_concurrency)

    async def execute(self, chunks: Iterable[ChunkRange]) -> list[ChunkResult]:
        semaphore = asyncio.Semaphore(self.max_concurrency)

        async def run(chunk: ChunkRange) -> ChunkResult:
            async with semaphore:
                return ChunkResult(
                    chunk=chunk,
                    data=await self.worker.fetch(chunk),
                )

        return list(await asyncio.gather(*(run(chunk) for chunk in chunks)))
