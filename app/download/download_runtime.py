from __future__ import annotations

from collections.abc import AsyncIterator

from .download_engine import DownloadEngine


class DownloadRuntime:
    """Runtime assembly layer for download execution.

    Keeps API routes away from concrete stream construction.
    """

    def __init__(self, engine: DownloadEngine) -> None:
        self.engine = engine

    async def stream(
        self,
        file_size: int,
        stream_factory,
        concurrent_factory,
    ) -> AsyncIterator[bytes]:
        async for chunk in self.engine.stream(
            file_size,
            stream_factory,
            concurrent_factory,
        ):
            yield chunk
