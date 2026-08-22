"""Account scheduling boundary for download execution.

The scheduler chooses Telegram accounts only. Network selection remains a
system-level concern owned by Telegram runtime.
"""

from dataclasses import dataclass, field
from typing import Iterable


@dataclass
class AccountState:
    account: object
    active_tasks: int = 0
    enabled: bool = True
    score: float = 0.0


class AccountScheduler:
    """Select an account for a download chunk/task.

    Future scoring can include speed, FloodWait and runtime health metrics.
    It deliberately does not handle proxy/network decisions.
    """

    def __init__(self, accounts: Iterable[object] | None = None) -> None:
        self.accounts = [AccountState(account=a) for a in (accounts or [])]

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


# Backward-compatible alias during migration.
AccountSelector = AccountScheduler
