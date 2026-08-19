"""Telegram scanner for tgStorage v2.

Converts Telegram messages into Resource records.
Does not handle API, UI, or download streaming.
"""

from datetime import datetime, timezone

from sqlalchemy import select

from app.v2.models.telegram import TelegramSource
from app.v2.models.resource import Resource
from app.v2.metadata.analyzer import ResourceAnalyzer
from app.v2.metadata.classifier import ResourceClassifier
from app.v2.metadata.category_resolver import CategoryResolver


class TelegramResourceScanner:
    """Index Telegram messages into v2 resource metadata."""

    def __init__(self, client, session, analyzer=None, classifier=None, category_resolver=None):
        self.client = client
        self.session = session
        self.analyzer = analyzer or ResourceAnalyzer()
        self.classifier = classifier or ResourceClassifier()
        self.category_resolver = category_resolver or CategoryResolver(session)

    async def scan_source(self, source: TelegramSource):
        last_id = source.last_message_id or 0
        count = 0

        async for message in self.client.iter_messages(
            source.chat_id,
            min_id=last_id,
        ):
            if not message.file:
                continue

            filename = message.file.name or f"{message.id}.bin"
            analysis = self.analyzer.analyze(
                filename,
                message.file.mime_type,
            )

            category_name = self.classifier.classify(
                filename,
                analysis["resource_type"],
                analysis["tags"],
            )
            category_id = await self.category_resolver.resolve(category_name)

            exists = await self.session.scalar(
                select(Resource).where(
                    Resource.source_id == source.id,
                    Resource.telegram_message_id == message.id,
                )
            )

            if exists:
                continue

            resource = Resource(
                source_id=source.id,
                telegram_message_id=message.id,
                filename=filename,
                extension=analysis["extension"],
                mime_type=message.file.mime_type or "",
                resource_type=analysis["resource_type"],
                tags_json=analysis["tags"],
                category_id=category_id,
                size=message.file.size or 0,
                status="active",
                created_at=datetime.now(timezone.utc),
            )

            self.session.add(resource)
            count += 1

            if message.id > last_id:
                last_id = message.id

        source.last_message_id = last_id
        source.last_scan_time = datetime.now(timezone.utc)

        await self.session.commit()

        return count
