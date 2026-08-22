from __future__ import annotations

from collections.abc import AsyncIterator

from app.download.providers import DownloadBackend, ResourceLocation


class DownloadService:
    """Application service coordinating resource streaming."""

    def __init__(self, backend: DownloadBackend):
        self.backend = backend

    async def stream(
        self,
        location: ResourceLocation,
        offset: int = 0,
        limit: int | None = None,
    ) -> AsyncIterator[bytes]:
        async for chunk in self.backend.stream(
            location,
            offset=offset,
            limit=limit,
        ):
            yield chunk
