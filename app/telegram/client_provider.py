"""DB-backed Telegram client provider."""
from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.account import TelegramAccount
from app.telegram.client_pool import TelegramClientPool
from app.telegram.runtime import TelegramClientRuntime

class DatabaseTelegramClientProvider:
    def __init__(self, session: AsyncSession, runtime: TelegramClientRuntime, pool: TelegramClientPool) -> None:
        self.session, self.runtime, self.pool = session, runtime, pool

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
        client = await self.runtime.connect(account)
        self.pool.register(account.id, client, status="online")
        account.status = "online"
        return client
