"""Administrative read-only API endpoints.

Phase 2-B initial version exposes resource management data without introducing
authentication or mutation operations yet.
"""

from fastapi import APIRouter
from sqlalchemy import select

from app.database import get_session
from app.models import Category, Resource, TelegramAccount, TelegramSource

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/accounts")
async def list_accounts():
    async with get_session() as session:
        result = await session.execute(select(TelegramAccount))
        return [
            {
                "id": account.id,
                "name": account.name,
                "status": account.status,
                "enabled": account.enabled,
                "last_login": account.last_login,
            }
            for account in result.scalars().all()
        ]


@router.get("/sources")
async def list_sources():
    async with get_session() as session:
        result = await session.execute(select(TelegramSource))
        return [
            {
                "id": source.id,
                "account_id": source.account_id,
                "chat_id": source.chat_id,
                "chat_type": source.chat_type,
                "title": source.title,
                "enabled": source.enabled,
                "sync_mode": source.sync_mode,
            }
            for source in result.scalars().all()
        ]


@router.get("/resources")
async def list_resources():
    async with get_session() as session:
        result = await session.execute(select(Resource))
        return [
            {
                "id": resource.id,
                "filename": resource.filename,
                "source_id": resource.source_id,
                "category_id": resource.category_id,
                "mime_type": resource.mime_type,
                "size": resource.size,
                "status": resource.status,
            }
            for resource in result.scalars().all()
        ]
