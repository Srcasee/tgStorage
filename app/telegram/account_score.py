"""Account scoring primitives for Telegram client scheduling.

This module intentionally keeps scoring independent from Telethon runtime.
The scheduler can later use these metrics to select the best available account.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class AccountScore:
    """Runtime health and performance metrics for one Telegram account."""

    account_id: int
    success_count: int = 0
    failure_count: int = 0
    flood_wait_count: int = 0
    total_bytes: int = 0
    total_seconds: float = 0.0
    last_used_at: datetime | None = None

    def record_success(self, size: int = 0, seconds: float = 0.0) -> None:
        self.success_count += 1
        self.total_bytes += max(size, 0)
        self.total_seconds += max(seconds, 0.0)
        self.last_used_at = datetime.now(timezone.utc)

    def record_failure(self, flood_wait: bool = False) -> None:
        self.failure_count += 1
        if flood_wait:
            self.flood_wait_count += 1
        self.last_used_at = datetime.now(timezone.utc)

    @property
    def speed(self) -> float:
        if self.total_seconds <= 0:
            return 0.0
        return self.total_bytes / self.total_seconds

    @property
    def score(self) -> float:
        """Simple scheduler score.

        Higher speed helps. Failures and flood waits reduce priority.
        This is deliberately deterministic and can be replaced later.
        """
        return (
            self.speed
            - (self.failure_count * 1024 * 1024)
            - (self.flood_wait_count * 10 * 1024 * 1024)
        )
