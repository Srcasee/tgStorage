"""Telegram dialog discovery and source binding service.

Phase 3-4.3: after an account is authorized, discover dialogs and bind
Telegram channels/groups into telegram_sources without manual insertion.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import TelegramAccount
from app.models.telegram import TelegramSource
from app.telegram.runtime import TelegramClientRuntime


class TelegramSourceDiscovery:
    def __init__(self, session: AsyncSession, runtime: TelegramClientRuntime):
        self.session = session
        self.runtime = runtime

    async def discover(self, account_id: int) -> list[TelegramSource]:
        account = await self.session.scalar(
            select(TelegramAccount).where(TelegramAccount.id == account_id)
        )
        if account is None:
            raise RuntimeError(f"telegram account {account_id} not found")

        client = await self.runtime.connect(account)
        if not await client.is_user_authorized():
            raise RuntimeError(f"telegram account {account_id} unauthorized")

        created: list[TelegramSource] = []

        async for dialog in client.iter_dialogs(limit=200):
            entity_type = type(dialog.entity).__name__
            if entity_type not in {"Channel", "Chat"}:
                continue

            exists = await self.session.scalar(
                select(TelegramSource).where(
                    TelegramSource.account_id == account_id,
                    TelegramSource.chat_id == dialog.id,
                )
            )

            if exists:
                continue

            source = TelegramSource(
                account_id=account_id,
                chat_id=dialog.id,
                chat_type="channel" if entity_type == "Channel" else "group",
                title=dialog.name or "",
                bound_chat_id=dialog.id,
                enabled=True,
            )
            self.session.add(source)
            created.append(source)

        await self.session.commit()
        return created
