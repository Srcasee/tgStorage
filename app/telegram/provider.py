"""Telegram client provider.

Keeps account lifecycle concerns outside scanner/indexer code.
"""

from __future__ import annotations

from telethon import TelegramClient

from app.models.account import TelegramAccount
from app.telegram.runtime import TelegramClientRuntime


class TelegramClientProvider:
    """Provide connected and authorized Telegram clients."""

    def __init__(self, runtime: TelegramClientRuntime):
        self.runtime = runtime

    async def get_client(self, account: TelegramAccount) -> TelegramClient:
        client = await self.runtime.connect(account)

        if not await client.is_user_authorized():
            raise RuntimeError(
                f"Telegram account {account.id} is not authorized; "
                "login is required before scanning"
            )

        return client
