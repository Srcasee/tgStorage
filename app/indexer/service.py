"""Telegram -> Resource indexer with explicit source boundaries."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.metadata.analyzer import ResourceAnalyzer
from app.metadata.category_resolver import CategoryResolver
from app.metadata.classifier import ResourceClassifier
from app.models.resource import Resource
from app.models.telegram import TelegramSource
from app.telegram.cleanup import TelegramResourceCleanup
from app.telegram.identity import normalize_chat_id


def is_indexable_message(message) -> bool:
    """Return True only for a live Telegram file message."""
    if not message or not getattr(message, "id", None):
        return False
    if getattr(message, "deleted", False):
        return False
    if not getattr(message, "media", None) or not getattr(message, "file", None):
        return False
    return getattr(message.file, "size", None) is not None


def validate_telegram_entity(source: TelegramSource, entity) -> None:
    """Strictly validate Telegram source identity."""
    entity_id = normalize_chat_id(int(getattr(entity, "id", 0)))
    if entity_id != int(source.chat_id):
        raise RuntimeError(
            f"telegram source binding mismatch: expected {source.chat_id}, got {entity_id}"
        )
    if source.chat_type == "group":
        if not bool(getattr(entity, "megagroup", False)):
            raise RuntimeError("telegram source is not a megagroup")
        if bool(getattr(entity, "broadcast", False)):
            raise RuntimeError("telegram group cannot be broadcast channel")
    elif source.chat_type == "channel":
        if not bool(getattr(entity, "broadcast", False)):
            raise RuntimeError("telegram source is not a broadcast channel")
        if bool(getattr(entity, "megagroup", False)):
            raise RuntimeError("telegram channel cannot be megagroup")

# Remaining indexer implementation intentionally unchanged.
