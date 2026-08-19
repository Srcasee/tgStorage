"""Minimal Telegram -> Resource indexer for tgStorage v2."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.v2.metadata.analyzer import ResourceAnalyzer
from app.v2.metadata.category_resolver import CategoryResolver
from app.v2.metadata.classifier import ResourceClassifier
from app.v2.models.resource import Resource
from app.v2.models.telegram import TelegramSource


class TelegramResourceIndexer:
    """Index Telegram file messages into the v2 Resource table."""

    def __init__(
        self,
        session: AsyncSession,
        analyzer: ResourceAnalyzer | None = None,
        classifier: ResourceClassifier | None = None,
    ) -> None:
        self.session = session
        self.analyzer = analyzer or ResourceAnalyzer()
        self.classifier = classifier or ResourceClassifier()
        self.categories = CategoryResolver(session)

    async def index_source(self, client, source: TelegramSource, limit: int = 200) -> int:
        result = await self.session.execute(
            select(Resource.telegram_message_id).where(
                Resource.source_id == source.id,
            )
        )
        existing = {row[0] for row in result.all() if row[0] is not None}

        indexed = 0
        async for message in client.iter_messages(source.chat_id, limit=limit):
            if not message or not message.file:
                continue
            if message.id in existing:
                continue

            filename = message.file.name or f"{message.id}.bin"
            mime_type = message.file.mime_type or ""
            metadata = self.analyzer.analyze(filename, mime_type)
            category_name = self.classifier.classify(
                filename,
                metadata["resource_type"],
                metadata["tags"],
            )
            category_id = await self.categories.resolve(category_name)

            self.session.add(
                Resource(
                    source_id=source.id,
                    telegram_message_id=message.id,
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
            existing.add(message.id)
            indexed += 1

        await self.session.commit()
        return indexed
