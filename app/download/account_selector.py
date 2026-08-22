"""Account scheduling boundary for download execution.

The scheduler chooses Telegram accounts only. Network selection remains a
system-level concern owned by Telegram runtime.
"""

from dataclasses import dataclass
from typing import Iterable


@dataclass
class AccountState:
    account: object
    active_tasks: int = 0
    enabled: bool = True
    score: float = 0.0


class AccountScheduler:
    """Select and track Telegram accounts for download execution."""

    def __init__(self, accounts: Iterable[object] | None = None) -> None:
        self.accounts: list[AccountState] = []
        self.refresh(accounts or [])

    def refresh(self, accounts: Iterable[object]) -> None:
        """Replace account snapshot without replacing scheduler state owner."""
        current = {
            item.account: item
            for item in self.accounts
        }
        self.accounts = []
        for account in accounts:
            state = current.get(account)
            self.accounts.append(state or AccountState(account=account))

    async def select(self) -> object | None:
        available = [
            item for item in self.accounts
            if item.enabled and getattr(item.account, "enabled", True)
        ]
        if not available:
            return None

        selected = min(
            available,
            key=lambda item: (item.active_tasks, -item.score),
        )
        selected.active_tasks += 1
        return selected.account

    async def release(self, account: object) -> None:
        for item in self.accounts:
            if item.account == account:
                item.active_tasks = max(0, item.active_tasks - 1)
                return


AccountSelector = AccountScheduler
