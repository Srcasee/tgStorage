"""Administrative API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependency import require_admin_api_key
from app.core.database import get_session
from app.models import Resource, TelegramAccount, TelegramSource
from app.models.network import NetworkPlugin
from app.network.registry import reload_network_selector

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin_api_key)],
)


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


class NetworkPluginUpdateRequest(BaseModel):
    enabled: bool


@router.get("/accounts")
async def list_accounts(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(TelegramAccount))
    return [{"id": x.id, "name": x.name, "status": x.status, "enabled": x.enabled, "last_login": x.last_login} for x in result.scalars().all()]


@router.post("/accounts")
async def create_account(payload: AccountCreateRequest, session: AsyncSession = Depends(get_session)):
    account = TelegramAccount(**payload.model_dump())
    session.add(account)
    await session.commit()
    await session.refresh(account)
    return {"id": account.id, "name": account.name}


@router.patch("/accounts/{account_id}")
async def update_account(account_id: int, enabled: bool, session: AsyncSession = Depends(get_session)):
    account = await session.get(TelegramAccount, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="account not found")
    account.enabled = enabled
    await session.commit()
    return {"id": account.id, "enabled": account.enabled}


@router.get("/sources")
async def list_sources(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(TelegramSource))
    return [{"id": x.id, "account_id": x.account_id, "chat_id": x.chat_id, "chat_type": x.chat_type, "title": x.title, "enabled": x.enabled, "sync_mode": x.sync_mode} for x in result.scalars().all()]


@router.post("/sources")
async def create_source(payload: SourceCreateRequest, session: AsyncSession = Depends(get_session)):
    source = TelegramSource(**payload.model_dump())
    session.add(source)
    await session.commit()
    await session.refresh(source)
    return {"id": source.id}


@router.get("/resources")
async def list_resources(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Resource))
    return [{"id": x.id, "filename": x.filename, "source_id": x.source_id, "category_id": x.category_id, "mime_type": x.mime_type, "size": x.size, "status": x.status} for x in result.scalars().all()]


@router.patch("/resources/{resource_id}")
async def update_resource_category(resource_id: int, payload: ResourceCategoryUpdateRequest, session: AsyncSession = Depends(get_session)):
    resource = await session.get(Resource, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="resource not found")
    resource.category_id = payload.category_id
    await session.commit()
    return {"id": resource.id, "category_id": resource.category_id}


@router.get("/network/plugins")
async def list_network_plugins(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(NetworkPlugin))
    return [
        {
            "id": x.id,
            "name": x.name,
            "type": x.type,
            "enabled": x.enabled,
            "priority": x.priority,
            "status": x.status,
        }
        for x in result.scalars().all()
    ]


@router.patch("/network/plugins/{plugin_id}")
async def update_network_plugin(plugin_id: int, payload: NetworkPluginUpdateRequest, session: AsyncSession = Depends(get_session)):
    plugin = await session.get(NetworkPlugin, plugin_id)
    if not plugin:
        raise HTTPException(status_code=404, detail="network plugin not found")
    plugin.enabled = payload.enabled
    await session.commit()
    return {"id": plugin.id, "enabled": plugin.enabled}


@router.post("/network/reload")
async def reload_network_plugins():
    return {"loaded": reload_network_selector()}
