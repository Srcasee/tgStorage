"""Telegram download backend adapter.

Keeps Telegram-specific streaming details behind the download backend boundary.
"""

from __future__ import annotations

from typing import AsyncIterator, Awaitable, Callable

from telethon import TelegramClient

from app.download.providers import DownloadBackend, ResourceLocation
from app.models.account import TelegramAccount
from app.telegram.provider import TelegramClientProvider


class TelegramBackend(DownloadBackend):
    """Backend adapter that reads bytes from Telegram runtime."""

    def __init__(
        self,
        client_provider: TelegramClientProvider,
        account_loader: Callable[[int], Awaitable[TelegramAccount]],
    ):
        self.client_provider = client_provider
        self.account_loader = account_loader

    async def stream(
        self,
        location: ResourceLocation,
        offset: int = 0,
        limit: int | None = None,
        chunk_size: int = 256 * 1024,
        account_id: int | None = None,
    ) -> AsyncIterator[bytes]:
        if account_id is None:
            raise ValueError("account_id is required for telegram backend")

        account = await self.account_loader(account_id)
        client: TelegramClient = await self.client_provider.get_client(account)

        message = await client.get_messages(
            location.chat_id,
            ids=location.message_id,
        )

        remaining = limit
        async for chunk in client.iter_download(
            message,
            offset=offset,
            request_size=chunk_size,
        ):
            if remaining is not None:
                if remaining <= 0:
                    break
                chunk = chunk[:remaining]
                remaining -= len(chunk)

            if chunk:
                yield bytes(chunk)
