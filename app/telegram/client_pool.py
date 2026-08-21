"""Telegram client pool abstraction for tgStorage v2.

Keeps Telegram client lifecycle separate from download logic.
The concrete Telethon wiring can be injected later.
"""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class TelegramClientEntry:
    account_id: int
    client: Any
    status: str = "offline"


class TelegramClientPool:
    """Manage reusable Telegram clients.

    This intentionally does not create clients itself. Authentication,
    proxy configuration and Telethon setup belong to the provider layer.
    """

    def __init__(self):
        self._clients: dict[int, TelegramClientEntry] = {}

    def register(self, account_id: int, client: Any, status: str = "online"):
        self._clients[account_id] = TelegramClientEntry(
            account_id=account_id,
            client=client,
            status=status,
        )

    def remove(self, account_id: int):
        self._clients.pop(account_id, None)

    def get_available(self, account_id: Optional[int] = None):
        if account_id:
            entry = self._clients.get(account_id)
            if entry and entry.status == "online":
                return entry
            return None

        for entry in self._clients.values():
            if entry.status == "online":
                return entry
        return None
