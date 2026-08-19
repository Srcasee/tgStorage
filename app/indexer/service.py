"""Minimal Telegram -> Resource indexer for tgStorage."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.metadata.analyzer import ResourceAnalyzer
from app.metadata.category_resolver import CategoryResolver
from app.metadata.classifier import ResourceClassifier
from app.models.resource import Resource
from app.models.telegram import TelegramSource


class TelegramResourceIndexer:
    """Index Telegram file messages into the Resource table."""

    def __init__(self, session: AsyncSession, analyzer=None, classifier=None) -> None:
        self.session = session
        self.analyzer = analyzer or ResourceAnalyzer()
        self.classifier = classifier or ResourceClassifier()
        self.categories = CategoryResolver(session)

    async def index_source(self, client, source: TelegramSource, limit: int = 200) -> int:
        result = await self.session.execute(
            select(Resource.telegram_message_id).where(Resource.source_id == source.id)
        )
        existing = {row[0] for row in result.all() if row[0] is not None}

        indexed = 0
        async for message in client.iter_messages(source.chat_id, limit=limit):
            if not message or not message.file or message.id in existing:
                continue

            filename = message.file.name or f"{message.id}.bin"
            mime_type = message.file.mime_type or ""
            metadata = self.analyzer.analyze(filename, mime_type)
            category_name = self.classifier.classify(
                filename, metadata["resource_type"], metadata["tags"]
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
