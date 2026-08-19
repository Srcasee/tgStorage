from __future__ import annotations

from typing import Protocol


class TelegramClientProvider(Protocol):
    async def get_client(self, account_id: int | None = None):
        ...


class TelegramFileProvider:
    """Adapter between Telegram clients and download engine.

    Real Telethon implementation will be injected here. Keeping this adapter
    separate allows account rotation and proxy plugins without changing the
    download pipeline.
    """

    def __init__(self, client_provider: TelegramClientProvider):
        self.client_provider = client_provider

    async def read_chunk(
        self,
        chat_id: int,
        message_id: int,
        offset: int,
        limit: int,
    ) -> bytes:
        client = await self.client_provider.get_client()

        # Placeholder adapter call. Concrete Telethon implementation should
        # provide the actual chunk reader.
        return await client.read_message_chunk(
            chat_id=chat_id,
            message_id=message_id,
            offset=offset,
            limit=limit,
        )
