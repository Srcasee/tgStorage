"""Runtime adapter for selecting Telegram accounts.

Keeps account selection separate from database and Telethon runtime. The
scheduler can later provide richer candidates backed by persistent metrics.
"""

from __future__ import annotations

from collections.abc import Iterable

from app.telegram.account_selector import AccountCandidate, AccountSelector


class RuntimeAccountSelector:
    """Small bridge between runtime account state and selector logic."""

    def __init__(self, selector: AccountSelector | None = None) -> None:
        self._selector = selector or AccountSelector()

    def choose(self, account_ids: Iterable[int]) -> int | None:
        candidates = (
            AccountCandidate(account_id=account_id)
            for account_id in account_ids
        )
        selected = self._selector.select(candidates)
        return selected.account_id if selected else None
