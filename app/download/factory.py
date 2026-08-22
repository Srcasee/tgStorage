"""Download runtime assembly helpers."""

from __future__ import annotations

from app.download.account_selector import AccountScheduler
from app.download.backend.telegram_backend import TelegramBackend
from app.download.backend.telegram_runtime_adapter import TelegramRuntimeAdapter
from app.download.service import DownloadService
from app.telegram.client_provider import DatabaseTelegramClientProvider
from app.telegram.runtime_registry import get_pool, get_runtime


async def load_accounts(provider):
    return await provider.list_accounts()


def create_download_service(session) -> DownloadService:
    """Create download service with isolated runtime dependencies."""
    provider = DatabaseTelegramClientProvider(
        session=session,
        runtime=get_runtime(),
        pool=get_pool(),
    )
    scheduler = AccountScheduler()
    runtime_adapter = TelegramRuntimeAdapter(
        provider,
        scheduler,
    )
    backend = TelegramBackend(runtime_adapter)
    return DownloadService(backend)
