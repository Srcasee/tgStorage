from collections.abc import AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import SessionLocal
from app.download.service import DownloadService


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield one database session per request."""
    async with SessionLocal() as session:
        yield session


async def get_download_service(request: Request) -> DownloadService:
    """Return the application-scoped download service."""
    return request.app.state.download_service
