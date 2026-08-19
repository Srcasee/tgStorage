from __future__ import annotations

from typing import AsyncIterator, Protocol


class TelegramClientProvider(Protocol):
    async def get_client(self, account_id: int | None = None):
        """Return an authenticated Telegram client."""
        ...


class TelegramFileProvider(Protocol):
    async def stream_message(
        self,
        chat_id: int,
        message_id: int,
        offset: int = 0,
        limit: int | None = None,
        chunk_size: int = 256 * 1024,
        account_id: int | None = None,
    ) -> AsyncIterator[bytes]:
        """Yield bytes from a Telegram message media file."""
        ...
