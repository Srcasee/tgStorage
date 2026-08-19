from __future__ import annotations

from typing import AsyncIterator

from .providers import TelegramClientProvider


class TelethonFileProvider:
    """Read Telegram media with Telethon's native async download iterator."""

    def __init__(self, client_provider: TelegramClientProvider):
        self.client_provider = client_provider

    async def validate_message(
        self,
        chat_id: int,
        message_id: int,
        account_id: int | None = None,
    ) -> None:
        """Validate that the Telegram message exists and contains media.

        This runs before a StreamingResponse is returned so a missing message
        can still be represented by a normal HTTP error instead of an
        exception raised after response headers have already been sent.
        """
        client = await self.client_provider.get_client(account_id)
        message = await client.get_messages(chat_id, ids=message_id)
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
        message = await client.get_messages(chat_id, ids=message_id)
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
