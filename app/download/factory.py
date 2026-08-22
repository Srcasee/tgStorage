"""Download runtime assembly helpers.

This module owns download service construction so API layers do not depend on
Telegram runtime implementation details.
"""

from __future__ import annotations

from app.download.backend.telegram_backend import TelegramBackend
from app.download.service import DownloadService
from app.telegram.client_provider import DatabaseTelegramClientProvider
from app.telegram.runtime_registry import get_pool, get_runtime


def create_download_service(session) -> DownloadService:
    """Create the application download service.

    Runtime and Telegram client dependencies are assembled here. Callers only
    provide application persistence context and receive a download service.
    """
    provider = DatabaseTelegramClientProvider(
        session=session,
        runtime=get_runtime(),
        pool=get_pool(),
    )
    backend = TelegramBackend(
        provider,
        lambda account: provider.get_account(account),
    )
    return DownloadService(backend)
