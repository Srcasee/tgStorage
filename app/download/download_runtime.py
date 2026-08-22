from __future__ import annotations

from collections.abc import AsyncIterator, Callable

from .download_engine import DownloadEngine
from .strategy import DownloadStrategySelector


class DownloadRuntime:
    """Runtime lifecycle boundary for download execution."""

    def __init__(self, engine: DownloadEngine) -> None:
        self.engine = engine

    async def stream(
        self,
        file_size: int,
        stream_factory: Callable[[], AsyncIterator[bytes]],
        concurrent_factory: Callable[[], AsyncIterator[bytes]],
    ) -> AsyncIterator[bytes]:
        async for chunk in self.engine.execute(
            file_size,
            stream_factory,
            concurrent_factory,
        ):
            yield chunk

    @classmethod
    def create(
        cls,
        selector: DownloadStrategySelector | None = None,
    ) -> "DownloadRuntime":
        return cls(
            engine=DownloadEngine(
                selector=selector or DownloadStrategySelector()
            )
        )
