"""Telegram -> Resource indexer with explicit source boundaries."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.metadata.analyzer import ResourceAnalyzer
from app.metadata.category_resolver import CategoryResolver
from app.metadata.classifier import ResourceClassifier
from app.models.resource import Resource
from app.models.telegram import TelegramSource
from app.telegram.cleanup import TelegramResourceCleanup


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
    entity_id = int(getattr(entity, "id", 0))
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


def refresh_resource_metadata(
    resource: Resource,
    *,
    filename: str,
    extension: str,
    mime_type: str,
    resource_type: str,
    tags: list[str],
    size: int,
    category_id: int | None,
) -> None:
    """Refresh mutable Telegram metadata on an existing Resource row."""
    resource.filename = filename
    resource.extension = extension
    resource.mime_type = mime_type
    resource.resource_type = resource_type
    resource.tags_json = tags
    resource.size = size
    resource.category_id = category_id
    resource.status = "active"


class TelegramResourceIndexer:
    """Index file messages from exactly one configured TelegramSource."""

    def __init__(self, session: AsyncSession, analyzer=None, classifier=None) -> None:
        self.session = session
        self.analyzer = analyzer or ResourceAnalyzer()
        self.classifier = classifier or ResourceClassifier()
        self.categories = CategoryResolver(session)

    async def index_source(self, client, source: TelegramSource, limit: int = 200) -> int:
        chat_id = int(source.chat_id)
        if source.bound_chat_id is None:
            source.bound_chat_id = chat_id
        elif int(source.bound_chat_id) != chat_id:
            await self.session.execute(
                Resource.__table__.update()
                .where(Resource.source_id == source.id)
                .values(status="unavailable")
            )
            source.bound_chat_id = chat_id
            source.last_scanned_message_id = 0

        entity = await client.get_entity(chat_id)
        validate_telegram_entity(source, entity)
        await TelegramResourceCleanup(self.session).reconcile()

        result = await self.session.execute(
            select(Resource).where(
                Resource.source_id == source.id,
                Resource.telegram_chat_id == chat_id,
            )
        )
        existing = {r.telegram_message_id: r for r in result.scalars()}
        full_reconcile = source.sync_mode == "full"
        cursor = source.last_scanned_message_id or 0
        seen_ids: set[int] = set()
        indexed = 0
        max_message_id = cursor

        kwargs = {"limit": None if full_reconcile else limit}
        if not full_reconcile:
            kwargs["min_id"] = cursor

        async for message in client.iter_messages(chat_id, **kwargs):
            message_id = int(message.id) if getattr(message, "id", None) else 0
            if not full_reconcile and message_id <= cursor:
                continue
            if not is_indexable_message(message):
                continue

            max_message_id = max(max_message_id, message_id)
            seen_ids.add(message_id)
            filename = message.file.name or f"{message_id}.bin"
            mime_type = message.file.mime_type or ""
            metadata = self.analyzer.analyze(filename, mime_type)
            category_name = self.classifier.classify(
                filename, metadata["resource_type"], metadata["tags"]
            )
            category_id = await self.categories.resolve(category_name)
            resource = existing.get(message_id)

            if resource is None:
                self.session.add(Resource(
                    source_id=source.id,
                    telegram_chat_id=chat_id,
                    telegram_message_id=message_id,
                    filename=filename,
                    extension=metadata["extension"],
                    mime_type=mime_type,
                    resource_type=metadata["resource_type"],
                    tags_json=metadata["tags"],
                    size=message.file.size or 0,
                    category_id=category_id,
                    status="active",
                ))
                indexed += 1
            else:
                refresh_resource_metadata(
                    resource,
                    filename=filename,
                    extension=metadata["extension"],
                    mime_type=mime_type,
                    resource_type=metadata["resource_type"],
                    tags=metadata["tags"],
                    size=message.file.size or 0,
                    category_id=category_id,
                )

        if full_reconcile:
            for message_id, resource in existing.items():
                if message_id not in seen_ids:
                    resource.status = "unavailable"

        source.last_scanned_message_id = max_message_id
        await self.session.commit()
        return indexed
