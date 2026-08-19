"""Compatibility entry point for Telegram scanning.

The active scanner lives in :mod:`app.indexer.service` and is invoked by
:class:`app.indexer.worker.TelegramIndexWorker`.

Important boundary:
- scan only TelegramSource rows explicitly enabled by the administrator;
- never enumerate arbitrary historical dialogs to discover sources;
- distinguish sources by (account_id, chat_id), not by title;
- incremental mode advances a per-source message cursor;
- full mode is an explicit reconciliation operation for one configured source;
- invalid/deleted messages are never indexed as active resources.

The pre-v2 dialog-enumerating implementation is preserved in
``scanner_legacy.py`` for rollback/reference and is not imported here.
"""

from app.indexer.service import TelegramResourceIndexer

__all__ = ["TelegramResourceIndexer"]
