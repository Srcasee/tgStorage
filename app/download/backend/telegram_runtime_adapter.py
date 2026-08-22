"""Telegram runtime adapter for download backend.

Keeps Telegram client and account runtime details outside the download backend.
"""

from __future__ import annotations

from typing import AsyncIterator

from telethon import TelegramClient

from app.download.providers import ResourceLocation
from app.models.account import TelegramAccount
from app.telegram.provider import TelegramClientProvider


class TelegramRuntimeAdapter:
    """Translate download requests into Telegram runtime operations."""

    def __init__(self, client_provider: TelegramClientProvider, account_loader):
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
            raise ValueError("account_id is required for telegram runtime")

        metadata = location.metadata or {}
        chat_id = metadata.get("chat_id")
        message_id = metadata.get("message_id")
        if chat_id is None or message_id is None:
            raise ValueError("telegram resource metadata requires chat_id and message_id")

        account: TelegramAccount = await self.account_loader(account_id)
        client: TelegramClient = await self.client_provider.get_client(account)
        message = await client.get_messages(chat_id, ids=message_id)

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
