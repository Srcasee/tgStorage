import asyncio

import pytest

from app.download.telethon_provider import TelethonFileProvider


class FakeClient:
    def __init__(self, message):
        self.message = message

    async def get_messages(self, chat_id, ids):
        return self.message


class FakeClientProvider:
    def __init__(self, client):
        self.client = client

    async def get_client(self, account_id=None):
        return self.client


def test_validate_message_rejects_missing_telegram_media():
    provider = TelethonFileProvider(FakeClientProvider(FakeClient(None)))

    with pytest.raises(FileNotFoundError, match="Telegram message or media was not found"):
        asyncio.run(provider.validate_message(chat_id=123, message_id=456))


def test_validate_message_accepts_telegram_media():
    message = type("Message", (), {"media": object()})()
    provider = TelethonFileProvider(FakeClientProvider(FakeClient(message)))

    asyncio.run(provider.validate_message(chat_id=123, message_id=456))
