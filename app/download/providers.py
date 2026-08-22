from __future__ import annotations

from dataclasses import dataclass
from typing import AsyncIterator, Protocol


@dataclass(frozen=True)
class ResourceLocation:
    """Backend-independent resource identifier."""

    resource_id: str
    backend: str
    metadata: dict[str, object] | None = None


class DownloadBackend(Protocol):
    async def stream(
        self,
        location: ResourceLocation,
        offset: int = 0,
        limit: int | None = None,
        chunk_size: int = 256 * 1024,
    ) -> AsyncIterator[bytes]:
        """Yield bytes from a backend resource."""
        ...


class TelegramClientProvider(Protocol):
    async def get_client(self, account_id: int | None = None):
        """Return an authenticated Telegram client from runtime layer."""
        ...


# Migration alias. New code should use DownloadBackend.
TelegramFileProvider = DownloadBackend
