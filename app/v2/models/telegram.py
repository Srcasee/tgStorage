"""Telegram related entities for v2.

ORM implementation will be added after migration strategy is finalized.
"""

from dataclasses import dataclass


@dataclass
class TelegramAccount:
    id: int | None = None
    name: str = ""
    session_path: str = ""
    enabled: bool = True


@dataclass
class TelegramSource:
    id: int | None = None
    account_id: int | None = None
    chat_id: int | None = None
    title: str = ""
