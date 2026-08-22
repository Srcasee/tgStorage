"""Download runtime assembly helpers."""

from __future__ import annotations

from app.download.backend.telegram_backend import TelegramBackend
from app.download.backend.telegram_runtime_adapter import TelegramRuntimeAdapter
from app.download.service import DownloadService
from app.telegram.client_provider import DatabaseTelegramClientProvider
from app.telegram.runtime_registry import get_pool, get_runtime


def create_download_service(session) -> DownloadService:
    """Create download service with isolated runtime dependencies."""
    provider = DatabaseTelegramClientProvider(
        session=session,
        runtime=get_runtime(),
        pool=get_pool(),
    )
    runtime_adapter = TelegramRuntimeAdapter(
        provider,
        lambda account: provider.get_account(account),
    )
    backend = TelegramBackend(runtime_adapter)
    return DownloadService(backend)
