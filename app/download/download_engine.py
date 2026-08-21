from __future__ import annotations

from collections.abc import AsyncIterator

from .strategy import DownloadStrategy, DownloadStrategySelector


class DownloadEngine:
    """Unified download execution entry point.

    Keeps API layer independent from concrete streaming strategies.
    """

    def __init__(self, selector: DownloadStrategySelector) -> None:
        self.selector = selector

    async def select_strategy(self, file_size: int) -> DownloadStrategy:
        return self.selector.select(file_size)

    async def stream(self, file_size: int, stream_factory, concurrent_factory) -> AsyncIterator[bytes]:
        strategy = self.selector.select(file_size)

        if strategy == DownloadStrategy.CONCURRENT:
            async for chunk in concurrent_factory():
                yield chunk
            return

        async for chunk in stream_factory():
            yield chunk
