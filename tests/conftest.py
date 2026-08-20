import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import get_session
from app.models import Base


@pytest.fixture
async def test_session_factory(tmp_path):
    db_file = tmp_path / "test.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_file}")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    yield factory

    await engine.dispose()


@pytest.fixture
async def override_database(test_session_factory):
    async def _override_get_session():
        async with test_session_factory() as session:
            yield session

    yield _override_get_session
