"""Download task orchestration for tgStorage v2.

This module keeps download scheduling separate from API and Telegram transport.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class DownloadTask:
    resource_id: int
    account_id: Optional[int] = None
    status: str = "pending"


class DownloadManager:
    """Coordinate resource lookup and backend selection.

    Backend selection and account scheduling are intentionally injected later
    through plugins so proxy/network strategies remain hot swappable.
    """

    def __init__(self, backend=None, account_selector=None):
        self.backend = backend
        self.account_selector = account_selector

    async def create_task(self, resource_id: int) -> DownloadTask:
        return DownloadTask(resource_id=resource_id)

    async def stream(self, task: DownloadTask):
        if not self.backend:
            raise RuntimeError("download backend is not configured")
        async for chunk in self.backend.stream(task):
            yield chunk
