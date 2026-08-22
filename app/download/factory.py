"""Download runtime assembly helpers.

This module owns download service construction so API layers do not depend on
Telegram runtime implementation details.
"""

from __future__ import annotations

from app.download.backend.telegram_backend import TelegramBackend
from app.download.service import DownloadService
from app.telegram.client_provider import DatabaseTelegramClientProvider


def create_download_service(session, runtime, pool) -> DownloadService:
    """Create the application download service.

    Telegram runtime dependencies are assembled here and are hidden from API
    callers.
    """
    provider = DatabaseTelegramClientProvider(
        session=session,
        runtime=runtime,
        pool=pool,
    )
    backend = TelegramBackend(
        provider,
        lambda account: provider.get_account(account),
    )
    return DownloadService(backend)
