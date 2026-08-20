"""Telegram -> Resource indexer with explicit source boundaries."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.metadata.analyzer import ResourceAnalyzer
from app.metadata.category_resolver import CategoryResolver
from app.metadata.classifier import ResourceClassifier
from app.models.resource import Resource
from app.models.telegram import TelegramSource
from app.telegram.identity import normalize_chat_id


def is_indexable_message(message) -> bool:
    if not message or getattr(message, "deleted", False):
        return False
    return bool(getattr(message, "media", None) and getattr(message, "file", None))


def validate_telegram_entity(source: TelegramSource, entity) -> None:
    entity_id = normalize_chat_id(int(getattr(entity, "id", 0)))
    if entity_id != int(source.chat_id):
        raise RuntimeError(
            f"telegram source binding mismatch: expected {source.chat_id}, got {entity_id}"
        )


def refresh_resource_metadata(
    resource,
    *,
    filename,
    extension,
    mime_type,
    resource_type,
    tags,
    size,
    category_id,
):
    resource.filename = filename
    resource.extension = extension
    resource.mime_type = mime_type
    resource.resource_type = resource_type
    resource.tags_json = tags
    resource.size = size
    resource.category_id = category_id
    resource.status = "active"


class TelegramResourceIndexer:
    def __init__(self, session: AsyncSession, analyzer=None, classifier=None):
        self.session = session
        self.analyzer = analyzer or ResourceAnalyzer()
        self.classifier = classifier or ResourceClassifier()
        self.categories = CategoryResolver(session)

    async def index_source(self, client, source: TelegramSource, limit: int = 200) -> int:
        chat_id = normalize_chat_id(int(source.chat_id))

        if source.bound_chat_id is not None and int(source.bound_chat_id) != chat_id:
            result = await self.session.execute(
                select(Resource).where(Resource.source_id == source.id)
            )
            for resource in result.scalars():
                resource.status = "unavailable"
            source.last_scanned_message_id = 0

        source.bound_chat_id = chat_id

        entity = await client.get_entity(chat_id)
        validate_telegram_entity(source, entity)

        result = await self.session.execute(
            select(Resource).where(Resource.source_id == source.id)
        )
        existing = {r.telegram_message_id: r for r in result.scalars()}

        cursor = source.last_scanned_message_id or 0
        created = 0
        max_id = cursor
        seen = set()

        kwargs = {"limit": None} if source.sync_mode == "full" else {
            "limit": limit,
            "min_id": cursor,
        }

        async for message in client.iter_messages(chat_id, **kwargs):
            if not is_indexable_message(message):
                continue

            message_id = int(message.id)
            if source.sync_mode != "full" and message_id <= cursor:
                continue

            max_id = max(max_id, message_id)
            seen.add(message_id)

            if message_id in existing:
                continue

            filename = message.file.name or f"{message_id}.bin"
            mime_type = message.file.mime_type or ""
            metadata = self.analyzer.analyze(filename, mime_type)
            category = await self.categories.resolve(
                self.classifier.classify(
                    filename,
                    metadata["resource_type"],
                    metadata["tags"],
                )
            )

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
                category_id=category,
                status="active",
            ))
            created += 1

        if source.sync_mode == "full":
            for message_id, resource in existing.items():
                if message_id not in seen:
                    resource.status = "unavailable"

        source.last_scanned_message_id = max_id
        await self.session.commit()
        return created
