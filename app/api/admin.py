"""Administrative API endpoints.

Phase 2-B exposed read-only management views.
Phase 2-C adds the first mutation endpoints while keeping the control plane
small and avoiding authentication coupling at this stage.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app.database import get_session
from app.models import Resource, TelegramAccount, TelegramSource

router = APIRouter(prefix="/admin", tags=["admin"])


class AccountCreateRequest(BaseModel):
    name: str
    session_path: str | None = None
    enabled: bool = True


class SourceCreateRequest(BaseModel):
    account_id: int
    chat_id: int
    chat_type: str = "channel"
    title: str | None = None
    sync_mode: str = "incremental"
    enabled: bool = True


class ResourceCategoryUpdateRequest(BaseModel):
    category_id: int | None = None


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


@router.post("/accounts")
async def create_account(payload: AccountCreateRequest):
    async with get_session() as session:
        account = TelegramAccount(
            name=payload.name,
            session_path=payload.session_path,
            enabled=payload.enabled,
        )
        session.add(account)
        await session.commit()
        await session.refresh(account)
        return {"id": account.id, "name": account.name}


@router.patch("/accounts/{account_id}")
async def update_account(account_id: int, enabled: bool):
    async with get_session() as session:
        account = await session.get(TelegramAccount, account_id)
        if not account:
            raise HTTPException(status_code=404, detail="account not found")
        account.enabled = enabled
        await session.commit()
        return {"id": account.id, "enabled": account.enabled}


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


@router.post("/sources")
async def create_source(payload: SourceCreateRequest):
    async with get_session() as session:
        source = TelegramSource(**payload.model_dump())
        session.add(source)
        await session.commit()
        await session.refresh(source)
        return {"id": source.id}


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


@router.patch("/resources/{resource_id}")
async def update_resource_category(resource_id: int, payload: ResourceCategoryUpdateRequest):
    async with get_session() as session:
        resource = await session.get(Resource, resource_id)
        if not resource:
            raise HTTPException(status_code=404, detail="resource not found")
        resource.category_id = payload.category_id
        await session.commit()
        return {"id": resource.id, "category_id": resource.category_id}
