"""DB-backed Telegram client provider.

Compatibility provider during migration. Account lookup stays database-backed,
while Telegram client lifecycle and authorization checks are delegated to the
runtime provider.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import TelegramAccount
from app.telegram.client_pool import TelegramClientPool
from app.telegram.provider import TelegramClientProvider


class TelegramClientAuthorizationError(RuntimeError):
    """Raised when an enabled Telegram account is not authorized."""


class DatabaseTelegramClientProvider:
    def __init__(self, session: AsyncSession, provider: TelegramClientProvider, pool: TelegramClientPool) -> None:
        self.session = session
        self.provider = provider
        self.pool = pool

    async def list_accounts(self):
        stmt = select(TelegramAccount).where(TelegramAccount.enabled.is_(True)).order_by(TelegramAccount.id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_client(self, account_id: int | None = None):
        stmt = select(TelegramAccount).where(TelegramAccount.enabled.is_(True))
        if account_id is not None:
            stmt = stmt.where(TelegramAccount.id == account_id)
        else:
            stmt = stmt.order_by(TelegramAccount.id).limit(1)

        result = await self.session.execute(stmt)
        account = result.scalar_one_or_none()
        if account is None:
            raise RuntimeError("no enabled Telegram account is available")

        try:
            client = await self.provider.get_client(account)
        except RuntimeError as exc:
            account.status = "unauthorized"
            await self.session.commit()
            raise TelegramClientAuthorizationError(str(exc)) from exc

        self.pool.register(account.id, client, status="online")
        account.status = "online"
        await self.session.commit()
        return client
