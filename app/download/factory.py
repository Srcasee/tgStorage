"""Download runtime assembly helpers.

This module keeps download-layer construction explicit without coupling the
chunk reader to Telegram runtime internals.
"""

from __future__ import annotations

from app.download.telegram_file_provider import RuntimeTelegramFileProvider


def create_telegram_file_provider(client_provider, account_loader):
    """Create the runtime-backed Telegram file provider.

    Dependencies remain explicit so application startup or tests can provide
    the appropriate Telegram runtime and account lookup implementation.
    """
    return RuntimeTelegramFileProvider(
        client_provider=client_provider,
        account_loader=account_loader,
    )
