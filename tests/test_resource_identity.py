import asyncio
from types import SimpleNamespace

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.indexer.service import TelegramResourceIndexer
from app.models.base import Base
from app.models.resource import Resource
from app.models.telegram import TelegramSource


class File:
    name = "example.zip"
    mime_type = "application/zip"
    size = 123


class Message:
    id = 1
    media = object()
    file = File()
    deleted = False


class Client:
    async def get_entity(self, chat_id):
        return SimpleNamespace(id=chat_id)

    async def iter_messages(self, chat_id, **kwargs):
        yield Message()


class Analyzer:
    def analyze(self, filename, mime_type):
        return {"extension": ".zip", "resource_type": "document", "tags": []}


class Classifier:
    def classify(self, filename, resource_type, tags):
        return None


async def make_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return engine, async_sessionmaker(engine, expire_on_commit=False)


def test_resource_identity_includes_telegram_chat_id():
    indexes = {
        item.name: tuple(column.name for column in item.columns)
        for item in Resource.__table__.indexes
        if item.unique
    }
    assert indexes["uq_resources_source_chat_message"] == (
        "source_id",
        "telegram_chat_id",
        "telegram_message_id",
    )


def test_scanner_persists_exact_source_chat_id():
    async def scenario():
        engine, Session = await make_session()
        async with Session() as session:
            source = TelegramSource(account_id=1, chat_id=-1004413553797)
            session.add(source)
            await session.commit()
            await session.refresh(source)

            count = await TelegramResourceIndexer(
                session, analyzer=Analyzer(), classifier=Classifier()
            ).index_source(Client(), source)

            assert count == 1
            resource = (await session.execute(select(Resource))).scalar_one()
            assert resource.telegram_chat_id == -1004413553797
            assert resource.telegram_message_id == 1

        await engine.dispose()

    asyncio.run(scenario())


def test_source_rebind_invalidates_old_resources_and_resets_cursor():
    async def scenario():
        engine, Session = await make_session()
        async with Session() as session:
            source = TelegramSource(
                account_id=1,
                chat_id=-1001,
                bound_chat_id=-1001,
                last_scanned_message_id=99,
            )
            session.add(source)
            await session.flush()
            old = Resource(
                source_id=source.id,
                telegram_chat_id=-1001,
                telegram_message_id=99,
                filename="old.zip",
                extension=".zip",
                mime_type="application/zip",
                resource_type="document",
                size=1,
                status="active",
            )
            session.add(old)
            await session.commit()

            source.chat_id = -1002
            await TelegramResourceIndexer(
                session, analyzer=Analyzer(), classifier=Classifier()
            ).index_source(Client(), source)

            await session.refresh(old)
            assert old.status == "unavailable"
            assert source.bound_chat_id == -1002
            assert source.last_scanned_message_id == 1

        await engine.dispose()

    asyncio.run(scenario())
