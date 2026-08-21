"""Download scheduling primitives for v2.

This module intentionally keeps scheduling independent from Telegram and
network implementations. It provides the layer where account scoring,
retry policy and parallel chunk strategies can be added later.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional


@dataclass
class DownloadTask:
    resource_id: int
    status: str = "queued"
    account_id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


class DownloadScheduler:
    """Select and track download tasks.

    The first implementation is intentionally simple. Future versions can
    score accounts by throughput, failures and proxy health.
    """

    def __init__(self):
        self.tasks: Dict[int, DownloadTask] = {}

    def create(self, resource_id: int) -> DownloadTask:
        task = DownloadTask(resource_id=resource_id)
        self.tasks[resource_id] = task
        return task

    def get(self, resource_id: int) -> Optional[DownloadTask]:
        return self.tasks.get(resource_id)

    def assign_account(self, resource_id: int, account_id: int) -> DownloadTask:
        task = self.tasks[resource_id]
        task.account_id = account_id
        task.status = "assigned"
        return task
