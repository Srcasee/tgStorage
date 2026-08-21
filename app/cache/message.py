"""Lightweight Telegram message cache.

Keeps frequently accessed message metadata in memory to avoid repeated
Telegram API lookups during range/download requests.
"""

from __future__ import annotations

from dataclasses import dataclass
import time
from collections import OrderedDict
from typing import Any


@dataclass
class CacheEntry:
    value: Any
    expires_at: float


class MessageCache:
    """Small LRU + TTL cache for Telegram message objects."""

    def __init__(self, max_items: int = 2048, ttl_seconds: int = 300):
        self.max_items = max_items
        self.ttl_seconds = ttl_seconds
        self._items: OrderedDict[str, CacheEntry] = OrderedDict()

    def get(self, key: str) -> Any | None:
        item = self._items.get(key)
        if item is None:
            return None

        if item.expires_at < time.time():
            self._items.pop(key, None)
            return None

        self._items.move_to_end(key)
        return item.value

    def set(self, key: str, value: Any) -> None:
        self._items[key] = CacheEntry(
            value=value,
            expires_at=time.time() + self.ttl_seconds,
        )
        self._items.move_to_end(key)

        while len(self._items) > self.max_items:
            self._items.popitem(last=False)

    def delete(self, key: str) -> None:
        self._items.pop(key, None)

    def clear(self) -> None:
        self._items.clear()


message_cache = MessageCache()
