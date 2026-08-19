"""DB-backed Telegram client provider."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.v2.models.account import TelegramAccount
from app.v2.telegram.client_pool import TelegramClientPool
from app.v2.telegram.runtime import TelegramClientRuntime


class DatabaseTelegramClientProvider:
    """Resolve an enabled account and return a connected Telethon client."""

    def __init__(
        self,
        session: AsyncSession,
        runtime: TelegramClientRuntime,
        pool: TelegramClientPool,
    ) -> None:
        self.session = session
        self.runtime = runtime
        self.pool = pool

    async def get_client(self, account_id: int | None = None):
        if account_id is not None:
            result = await self.session.execute(
                select(TelegramAccount).where(
                    TelegramAccount.id == account_id,
                    TelegramAccount.enabled.is_(True),
                )
            )
            account = result.scalar_one_or_none()
        else:
            result = await self.session.execute(
                select(TelegramAccount)
                .where(TelegramAccount.enabled.is_(True))
                .order_by(TelegramAccount.id)
                .limit(1)
            )
            account = result.scalar_one_or_none()

        if account is None:
            raise RuntimeError("no enabled Telegram account is available")

        client = await self.runtime.connect(account)
        self.pool.register(account.id, client, status="online")
        account.status = "online"
        return client
