"""Download worker abstraction.

Workers consume chunk assignments and delegate actual IO to a backend.
No Telegram or proxy logic is placed here.
"""

from dataclasses import dataclass
from typing import Optional

from .chunk_manager import ChunkRange


@dataclass
class ChunkTask:
    resource_id: int
    chunk: ChunkRange
    account_id: Optional[int] = None
    status: str = "queued"


class DownloadWorker:
    def __init__(self, backend):
        self.backend = backend

    async def fetch_chunk(self, task: ChunkTask):
        """Fetch one chunk through the configured backend."""
        return await self.backend.read_chunk(
            resource_id=task.resource_id,
            start=task.chunk.start,
            end=task.chunk.end,
            account_id=task.account_id,
        )
