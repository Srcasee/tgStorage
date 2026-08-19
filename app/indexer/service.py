"""Telegram -> Resource indexer with explicit source boundaries.

The indexer intentionally does *not* enumerate Telegram dialogs. A source is
scanned only when an administrator has created/enabled its TelegramSource row.
This prevents a logged-in account's historical dialog cache from becoming an
implicit discovery scope.
"""

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.metadata.analyzer import ResourceAnalyzer
from app.metadata.category_resolver import CategoryResolver
from app.metadata.classifier import ResourceClassifier
from app.models.resource import Resource
from app.models.telegram import TelegramSource


class TelegramResourceIndexer:
    """Index currently valid file messages from one explicitly configured source."""

    def __init__(self, session: AsyncSession, analyzer=None, classifier=None) -> None:
        self.session = session
        self.analyzer = analyzer or ResourceAnalyzer()
        self.classifier = classifier or ResourceClassifier()
        self.categories = CategoryResolver(session)

    async def index_source(self, client, source: TelegramSource, limit: int = 200) -> int:
        """Index one configured source.

        ``incremental`` mode reads only messages newer than the source cursor.
        ``full`` mode is an explicit reconciliation and reads the complete
        history of this configured source. No other dialogs are inspected.
        """
        # Validate that the configured chat is still accessible. This is an
        # entity lookup, not dialog enumeration, and therefore cannot expand
        # the scan scope beyond this source.
        await client.get_entity(source.chat_id)

        result = await self.session.execute(
            select(Resource).where(Resource.source_id == source.id)
        )
        existing = {resource.telegram_message_id: resource for resource in result.scalars()}

        full_reconcile = source.sync_mode == "full"
        cursor = source.last_scanned_message_id or 0
        seen_ids: set[int] = set()
        indexed = 0
        max_message_id = cursor

        message_kwargs = {}
        if full_reconcile:
            # Full mode is deliberately explicit and source-scoped. It is the
            # only mode allowed to reconcile historical resources.
            message_kwargs["limit"] = None
        else:
            message_kwargs["min_id"] = cursor
            message_kwargs["limit"] = limit

        async for message in client.iter_messages(source.chat_id, **message_kwargs):
            if not message or not getattr(message, "id", None):
                continue

            message_id = int(message.id)
            max_message_id = max(max_message_id, message_id)

            # Telegram may return service/empty messages in history. They are
            # not resources and must not move the resource into the active set.
            if getattr(message, "deleted", False):
                continue
            if not message.media or not message.file:
                continue
            if message.file.size is None:
                continue

            seen_ids.add(message_id)
            resource = existing.get(message_id)
            filename = message.file.name or f"{message_id}.bin"
            mime_type = message.file.mime_type or ""
            metadata = self.analyzer.analyze(filename, mime_type)
            category_name = self.classifier.classify(
                filename, metadata["resource_type"], metadata["tags"]
            )
            category_id = await self.categories.resolve(category_name)

            if resource is not None:
                # A resource previously marked unavailable may become valid
                # again if Telegram exposes the message/media once more.
                resource.status = "active"
                resource.filename = filename
                resource.extension = metadata["extension"]
                resource.mime_type = mime_type
                resource.resource_type = metadata["resource_type"]
                resource.tags_json = metadata["tags"]
                resource.size = message.file.size or 0
                resource.category_id = category_id
            else:
                self.session.add(
                    Resource(
                        source_id=source.id,
                        telegram_message_id=message_id,
                        filename=filename,
                        extension=metadata["extension"],
                        mime_type=mime_type,
                        resource_type=metadata["resource_type"],
                        tags_json=metadata["tags"],
                        size=message.file.size or 0,
                        category_id=category_id,
                        status="active",
                    )
                )
                indexed += 1

        if full_reconcile:
            # Because full mode enumerated the complete history of this exact
            # source, anything previously indexed but not seen is no longer a
            # currently valid resource. Keep it for audit/history, but hide it
            # from normal search and download.
            for message_id, resource in existing.items():
                if message_id is not None and message_id not in seen_ids:
                    resource.status = "unavailable"

        source.last_scanned_message_id = max_message_id
        await self.session.commit()
        return indexed
