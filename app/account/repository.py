"""Account data access boundary."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import TelegramAccount


class AccountRepository:
    """Database access for Telegram account metadata.

    The repository owns account persistence only. Runtime client creation and
    scheduling remain outside this layer.
    """

    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def list_enabled(self) -> list[TelegramAccount]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(TelegramAccount)
                .where(TelegramAccount.enabled.is_(True))
                .order_by(TelegramAccount.id)
            )
            return list(result.scalars().all())

    async def get(self, account_id: int) -> TelegramAccount | None:
        async with self.session_factory() as session:
            result = await session.execute(
                select(TelegramAccount).where(TelegramAccount.id == account_id)
            )
            return result.scalar_one_or_none()

    async def update_status(self, account_id: int, status: str) -> None:
        async with self.session_factory() as session:
            account = await session.get(TelegramAccount, account_id)
            if account is None:
                return
            account.status = status
            await session.commit()
