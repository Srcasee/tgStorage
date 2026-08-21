import asyncio

from sqlalchemy import select

from app.models.resource import Resource
from app.telegram.cleanup import TelegramResourceCleanup

from tests.test_scanner_boundaries import make_session
from app.models.telegram import TelegramSource



def test_cleanup_invalidates_cross_chat_resources():
    async def scenario():
        engine, Session = await make_session()
        async with Session() as session:
            source = TelegramSource(
                account_id=1,
                chat_id=-1004413553797,
                chat_type="group",
                title="My Documents",
                enabled=True,
            )
            session.add(source)
            await session.flush()

            session.add(Resource(
                source_id=source.id,
                telegram_chat_id=-1004368336866,
                telegram_message_id=1,
                filename="wrong.txt",
                extension="txt",
                mime_type="text/plain",
                resource_type="document",
                size=1,
                status="active",
            ))
            await session.commit()

            changed = await TelegramResourceCleanup(session).reconcile()
            assert changed == 1

            rows = (await session.execute(select(Resource))).scalars().all()
            assert rows[0].status == "unavailable"

        await engine.dispose()

    asyncio.run(scenario())
