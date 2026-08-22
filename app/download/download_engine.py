from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Callable

from .strategy import DownloadStrategySelector


class DownloadEngine:
    """Execution coordinator for download tasks.

    The engine decides execution flow but does not know Telegram,
    proxy, or concrete storage implementations.
    """

    def __init__(self, selector: DownloadStrategySelector) -> None:
        self.selector = selector

    async def execute(
        self,
        file_size: int,
        stream_factory: Callable[[], AsyncIterator[bytes]],
        concurrent_factory: Callable[[], AsyncIterator[bytes]],
    ) -> AsyncIterator[bytes]:
        strategy = self.selector.select(file_size)

        factory = (
            concurrent_factory
            if strategy.value == "concurrent"
            else stream_factory
        )

        async for chunk in factory():
            yield chunk
