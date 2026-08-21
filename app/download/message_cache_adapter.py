from __future__ import annotations

from typing import Any

from app.cache.message import MessageCache


class DownloadMessageCache:
    """Small adapter used by download components to access Telegram message cache.

    Keeps cache concerns outside Telegram providers so download scheduling can be
    evolved without coupling cache implementation to Telethon.
    """

    def __init__(self, cache: MessageCache | None = None):
        self._cache = cache or MessageCache()

    def get(self, chat_id: int, message_id: int) -> Any | None:
        return self._cache.get((chat_id, message_id))

    def set(self, chat_id: int, message_id: int, message: Any) -> None:
        self._cache.set((chat_id, message_id), message)

    def clear(self) -> None:
        self._cache.clear()
