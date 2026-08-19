import asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.indexer.service import TelegramResourceIndexer
from app.models.base import Base
from app.models.resource import Resource
from app.models.telegram import TelegramSource


class FakeFile:
    def __init__(self, name="file.txt", mime_type="text/plain", size=10):
        self.name = name
        self.mime_type = mime_type
        self.size = size


class FakeMessage:
    def __init__(self, message_id, file=None, media=True, deleted=False):
        self.id = message_id
        self.file = file
        self.media = media
        self.deleted = deleted


class FakeClient:
    def __init__(self, messages):
        self.messages = messages
        self.iter_kwargs = None
        self.entity_ids = []

    async def get_entity(self, chat_id):
        self.entity_ids.append(chat_id)
        return object()

    async def iter_messages(self, chat_id, **kwargs):
        self.iter_kwargs = (chat_id, kwargs)
        for message in self.messages:
            yield message


class FakeAnalyzer:
    def analyze(self, filename, mime_type):
        return {
            "extension": ".txt",
            "resource_type": "document",
            "tags": [],
        }


class FakeClassifier:
    def classify(self, filename, resource_type, tags):
        return None


async def make_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return engine, async_sessionmaker(engine, expire_on_commit=False)


def test_incremental_scanner_is_source_bound_and_advances_cursor():
    async def scenario():
        engine, Session = await make_session()
        async with Session() as session:
            source = TelegramSource(
                account_id=1,
                chat_id=-1001,
                chat_type="channel",
                title="Documents",
                sync_mode="incremental",
                enabled=True,
                last_scanned_message_id=10,
            )
            session.add(source)
            await session.commit()
            await session.refresh(source)

            client = FakeClient(
                [
                    FakeMessage(12, FakeFile("new.txt")),
                    FakeMessage(11, file=None, media=None),
                    FakeMessage(10, FakeFile("old.txt")),
                ]
            )
            count = await TelegramResourceIndexer(
                session,
                analyzer=FakeAnalyzer(),
                classifier=FakeClassifier(),
            ).index_source(client, source)

            assert count == 1
            assert client.entity_ids == [-1001]
            assert client.iter_kwargs == (-1001, {"min_id": 10, "limit": 200})
            assert source.last_scanned_message_id == 12

            resources = list((await session.execute(Resource.__table__.select())).mappings())
            assert [row["telegram_message_id"] for row in resources] == [12]

        await engine.dispose()

    asyncio.run(scenario())


def test_full_mode_reconciles_only_the_configured_source():
    async def scenario():
        engine, Session = await make_session()
        async with Session() as session:
            source = TelegramSource(
                account_id=1,
                chat_id=-1002,
                chat_type="group",
                title="Documents",
                sync_mode="full",
                enabled=True,
                last_scanned_message_id=20,
            )
            session.add(source)
            await session.flush()
            old = Resource(
                source_id=source.id,
                telegram_message_id=20,
                filename="deleted.txt",
                extension=".txt",
                mime_type="text/plain",
                resource_type="document",
                size=10,
                status="active",
            )
            session.add(old)
            await session.commit()

            client = FakeClient([FakeMessage(21, FakeFile("current.txt"))])
            count = await TelegramResourceIndexer(
                session,
                analyzer=FakeAnalyzer(),
                classifier=FakeClassifier(),
            ).index_source(client, source)

            assert count == 1
            assert client.iter_kwargs == (-1002, {"limit": None})
            assert old.status == "unavailable"
            assert source.last_scanned_message_id == 21

        await engine.dispose()

    asyncio.run(scenario())
