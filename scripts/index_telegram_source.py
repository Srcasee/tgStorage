"""Run a real TelegramSource indexing pass.

Usage:
    ACCOUNT_ID=1 SOURCE_ID=1 python -m scripts.index_telegram_source
"""

from __future__ import annotations

import asyncio
import os

from sqlalchemy import select

from app.core.database import async_session_factory
from app.models.account import TelegramAccount
from app.models.telegram import TelegramSource
from app.telegram.runtime_registry import get_provider
from app.indexer.service import TelegramResourceIndexer


async def main() -> None:
    account_id = int(os.environ["ACCOUNT_ID"])
    source_id = int(os.environ["SOURCE_ID"])

    async with async_session_factory() as session:
        account = (
            await session.execute(
                select(TelegramAccount).where(TelegramAccount.id == account_id)
            )
        ).scalar_one()

        source = (
            await session.execute(
                select(TelegramSource).where(TelegramSource.id == source_id)
            )
        ).scalar_one()

        client = await get_provider().get_client(account)

        count = await TelegramResourceIndexer(session).index_source(
            client,
            source,
        )

        print(f"indexed={count} source={source.id} chat={source.chat_id}")


if __name__ == "__main__":
    asyncio.run(main())
