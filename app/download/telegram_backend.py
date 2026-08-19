"""Telegram streaming backend foundation for tgStorage v2.

The backend keeps Telegram transport isolated from the download API. A real
Telethon client provider can be injected later without changing the API layer.
"""

from dataclasses import dataclass
from typing import AsyncIterator, Optional


@dataclass
class TelegramFileLocator:
    chat_id: int
    message_id: int


class TelegramStreamBackend:
    """Stream Telegram resources through an injected client provider."""

    def __init__(self, client_provider=None):
        self.client_provider = client_provider

    async def locate(self, resource) -> TelegramFileLocator:
        if not getattr(resource, "telegram_message_id", None):
            raise ValueError("resource has no telegram message id")

        source = getattr(resource, "source", None)
        if not source or not getattr(source, "chat_id", None):
            raise ValueError("resource source has no telegram chat id")

        return TelegramFileLocator(
            chat_id=source.chat_id,
            message_id=resource.telegram_message_id,
        )

    async def stream(self, task) -> AsyncIterator[bytes]:
        """Yield file chunks.

        Actual Telegram IO is delegated to client_provider to keep proxy and
        account selection as pluggable components.
        """
        if not self.client_provider:
            raise RuntimeError("telegram client provider is not configured")

        async for chunk in self.client_provider.stream(task):
            yield chunk
