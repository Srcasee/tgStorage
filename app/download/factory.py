"""Download runtime assembly helpers."""

from __future__ import annotations

from app.account.repository import AccountRepository
from app.core.database import SessionLocal
from app.download.account_selector import AccountScheduler
from app.download.backend.telegram_backend import TelegramBackend
from app.download.backend.telegram_runtime_adapter import TelegramRuntimeAdapter
from app.download.service import DownloadService
from app.telegram.provider import TelegramClientProvider
from app.telegram.runtime_registry import get_runtime


async def create_download_service(session=None) -> DownloadService:
    """Create download service with isolated runtime dependencies."""
    repository = AccountRepository(SessionLocal)
    accounts = await repository.list_enabled()
    scheduler = AccountScheduler(accounts)

    provider = TelegramClientProvider(
        runtime=get_runtime(),
    )
    runtime_adapter = TelegramRuntimeAdapter(
        provider,
        scheduler,
    )
    backend = TelegramBackend(runtime_adapter)
    return DownloadService(backend)
