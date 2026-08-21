from __future__ import annotations

from collections.abc import AsyncIterator, Callable

from .download_engine import DownloadEngine
from .strategy import DownloadStrategySelector


class DownloadRuntime:
    """Factory and execution boundary for download flows.

    Keeps API routes independent from concrete stream implementations.
    """

    def __init__(
        self,
        engine: DownloadEngine,
        selector: DownloadStrategySelector | None = None,
    ) -> None:
        self.engine = engine
        self.selector = selector or DownloadStrategySelector()

    async def stream(
        self,
        file_size: int,
        stream_factory: Callable[[], AsyncIterator[bytes]],
        concurrent_factory: Callable[[], AsyncIterator[bytes]],
    ) -> AsyncIterator[bytes]:
        async for chunk in self.engine.stream(
            file_size,
            stream_factory,
            concurrent_factory,
        ):
            yield chunk

    @classmethod
    def create(
        cls,
        *,
        stream_factory: Callable[[], AsyncIterator[bytes]],
        concurrent_factory: Callable[[], AsyncIterator[bytes]],
        selector: DownloadStrategySelector | None = None,
    ) -> "DownloadRuntime":
        return cls(
            engine=DownloadEngine(selector=selector),
            selector=selector,
        )
