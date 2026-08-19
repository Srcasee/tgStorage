from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.v2.core.database import SessionLocal


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield one database session per request."""
    async with SessionLocal() as session:
        yield session
