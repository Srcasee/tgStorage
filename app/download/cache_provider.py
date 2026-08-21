from __future__ import annotations

from functools import lru_cache

from .message_cache_adapter import DownloadMessageCache


@lru_cache(maxsize=1)
def get_download_message_cache() -> DownloadMessageCache:
    """Return the shared download message cache instance.

    The cache is intentionally process-scoped. This allows multiple download
    requests handled by the same API worker to reuse Telegram message
    metadata while keeping the cache implementation replaceable later.
    """
    return DownloadMessageCache()
