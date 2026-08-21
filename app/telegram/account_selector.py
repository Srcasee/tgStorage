"""Account selection primitives for Telegram download scheduling.

This module intentionally contains no Telethon or database dependency. It provides
small deterministic selection helpers that can later be connected to the download
scheduler and persistent account metrics.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(slots=True)
class AccountCandidate:
    """Runtime view of an available Telegram account."""

    account_id: int
    score: float = 0.0
    available: bool = True


class AccountSelector:
    """Select the best available Telegram account.

    The scheduler can later replace the score source with the persistent
    AccountScore service without changing callers.
    """

    def select(self, accounts: Iterable[AccountCandidate]) -> AccountCandidate | None:
        available = [account for account in accounts if account.available]
        if not available:
            return None
        return max(available, key=lambda account: account.score)
