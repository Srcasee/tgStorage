"""Small background worker for the v2 Telegram indexer."""

import asyncio

from sqlalchemy import select

from app.v2.core.database import SessionLocal
from app.v2.models.telegram import TelegramSource
from app.v2.telegram.client_provider import DatabaseTelegramClientProvider
from app.v2.telegram.runtime_registry import get_runtime, get_pool
from app.v2.indexer.service import TelegramResourceIndexer


class TelegramIndexWorker:
    def __init__(self, interval: int = 300, batch_size: int = 200) -> None:
        self.interval = interval
        self.batch_size = batch_size
        self._task: asyncio.Task | None = None
        self._stopping = False

    def start(self) -> None:
        if self._task is None:
            self._stopping = False
            self._task = asyncio.create_task(self.run())

    async def stop(self) -> None:
        self._stopping = True
        if self._task is None:
            return
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        finally:
            self._task = None

    async def run(self) -> None:
        while not self._stopping:
            try:
                await self.scan_once()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                print(f"[V2 INDEX] {exc!r}", flush=True)
            await asyncio.sleep(self.interval)

    async def scan_once(self) -> None:
        async with SessionLocal() as session:
            result = await session.execute(
                select(TelegramSource).where(TelegramSource.enabled.is_(True))
            )
            sources = list(result.scalars().all())
            runtime = get_runtime()
            pool = get_pool()

            for source in sources:
                provider = DatabaseTelegramClientProvider(session, runtime, pool)
                client = await provider.get_client(source.account_id)
                indexer = TelegramResourceIndexer(session)
                count = await indexer.index_source(client, source, self.batch_size)
                if count:
                    print(
                        f"[V2 INDEX] source={source.id} indexed={count}",
                        flush=True,
                    )
