"""Administrative API endpoints.

Phase 2-B exposed read-only management views.
Phase 2-C adds the first mutation endpoints while keeping the control plane
small and avoiding authentication coupling at this stage.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app.core.database import get_session
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
        return [{"id": x.id, "name": x.name, "status": x.status, "enabled": x.enabled, "last_login": x.last_login} for x in result.scalars().all()]


@router.post("/accounts")
async def create_account(payload: AccountCreateRequest):
    async with get_session() as session:
        account = TelegramAccount(**payload.model_dump())
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
        return [{"id": x.id, "account_id": x.account_id, "chat_id": x.chat_id, "chat_type": x.chat_type, "title": x.title, "enabled": x.enabled, "sync_mode": x.sync_mode} for x in result.scalars().all()]


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
        return [{"id": x.id, "filename": x.filename, "source_id": x.source_id, "category_id": x.category_id, "mime_type": x.mime_type, "size": x.size, "status": x.status} for x in result.scalars().all()]


@router.patch("/resources/{resource_id}")
async def update_resource_category(resource_id: int, payload: ResourceCategoryUpdateRequest):
    async with get_session() as session:
        resource = await session.get(Resource, resource_id)
        if not resource:
            raise HTTPException(status_code=404, detail="resource not found")
        resource.category_id = payload.category_id
        await session.commit()
        return {"id": resource.id, "category_id": resource.category_id}
