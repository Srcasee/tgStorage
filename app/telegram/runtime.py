"""Lightweight Telethon client lifecycle for tgStorage."""

from __future__ import annotations

from dataclasses import dataclass

from telethon import TelegramClient

from app.models.account import TelegramAccount
from app.network.selector import NetworkSelector


@dataclass(frozen=True)
class TelegramClientConfig:
    api_id: int
    api_hash: str


class TelegramClientRuntime:
    def __init__(self, config: TelegramClientConfig, network_selector: NetworkSelector | None = None):
        self.config = config
        self.network_selector = network_selector or NetworkSelector()
        self._clients: dict[int, TelegramClient] = {}

    def get_or_create(self, account: TelegramAccount, network_type: str | None = None) -> TelegramClient:
        client = self._clients.get(account.id)
        if client is None:
            plugin = self.network_selector.select(network_type)
            client = TelegramClient(
                account.session_path,
                self.config.api_id,
                self.config.api_hash,
                **(plugin.client_options() if plugin else {}),
            )
            self._clients[account.id] = client
        return client

    async def connect(self, account: TelegramAccount, network_type: str | None = None) -> TelegramClient:
        client = self.get_or_create(account, network_type)
        if not client.is_connected():
            await client.connect()
        return client

    async def disconnect(self, account_id: int) -> None:
        client = self._clients.pop(account_id, None)
        if client is not None:
            await client.disconnect()

    async def disconnect_all(self) -> None:
        clients = list(self._clients.values())
        self._clients.clear()
        for client in clients:
            await client.disconnect()
