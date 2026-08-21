from __future__ import annotations

from typing import AsyncIterator

from .message_cache_adapter import DownloadMessageCache
from .providers import TelegramClientProvider


class TelethonFileProvider:
    """Read Telegram media with Telethon's native async download iterator."""

    def __init__(
        self,
        client_provider: TelegramClientProvider,
        message_cache: DownloadMessageCache | None = None,
    ):
        self.client_provider = client_provider
        self.message_cache = message_cache or DownloadMessageCache()

    async def _get_message(self, chat_id: int, message_id: int, account_id: int | None = None):
        cached = self.message_cache.get(chat_id, message_id)
        if cached is not None:
            return cached

        client = await self.client_provider.get_client(account_id)
        message = await client.get_messages(chat_id, ids=message_id)
        if message is not None:
            self.message_cache.set(chat_id, message_id, message)
        return message

    async def validate_message(
        self,
        chat_id: int,
        message_id: int,
        account_id: int | None = None,
    ) -> None:
        """Validate that the Telegram message exists and contains media."""
        message = await self._get_message(chat_id, message_id, account_id)
        if message is None or not getattr(message, "media", None):
            raise FileNotFoundError("Telegram message or media was not found")

    async def stream_message(
        self,
        chat_id: int,
        message_id: int,
        offset: int = 0,
        limit: int | None = None,
        chunk_size: int = 256 * 1024,
        account_id: int | None = None,
    ) -> AsyncIterator[bytes]:
        client = await self.client_provider.get_client(account_id)
        message = await self._get_message(chat_id, message_id, account_id)
        if message is None or not getattr(message, "media", None):
            raise FileNotFoundError("Telegram message or media was not found")

        remaining = limit
        async for chunk in client.iter_download(
            message.media,
            offset=offset,
            request_size=chunk_size,
        ):
            if remaining is None:
                yield chunk
                continue
            if remaining <= 0:
                break
            if len(chunk) > remaining:
                yield chunk[:remaining]
                break
            yield chunk
            remaining -= len(chunk)
