"""Telegram runtime adapter for download backend.

Keeps Telegram client and account runtime details outside the download backend.
"""

from __future__ import annotations

from typing import AsyncIterator

from telethon import TelegramClient

from app.download.account_selector import AccountScheduler
from app.download.providers import ResourceLocation
from app.models.account import TelegramAccount
from app.telegram.provider import TelegramClientProvider


class TelegramRuntimeAdapter:
    """Translate download requests into Telegram runtime operations."""

    def __init__(
        self,
        client_provider: TelegramClientProvider,
        account_scheduler: AccountScheduler,
    ):
        self.client_provider = client_provider
        self.account_scheduler = account_scheduler

    async def stream(
        self,
        location: ResourceLocation,
        offset: int = 0,
        limit: int | None = None,
        chunk_size: int = 256 * 1024,
    ) -> AsyncIterator[bytes]:
        account = await self.account_scheduler.select()
        if account is None:
            raise RuntimeError("no available telegram account")

        try:
            metadata = location.metadata or {}
            chat_id = metadata.get("chat_id")
            message_id = metadata.get("message_id")
            if chat_id is None or message_id is None:
                raise ValueError("telegram resource metadata requires chat_id and message_id")

            account_model: TelegramAccount = account
            client: TelegramClient = await self.client_provider.get_client(account_model)
            message = await client.get_messages(chat_id, ids=message_id)

            if message is None or not message.media:
                raise ValueError("telegram message has no downloadable media")

            remaining = limit
            async for chunk in client.iter_download(
                message.media,
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
        finally:
            await self.account_scheduler.release(account)
