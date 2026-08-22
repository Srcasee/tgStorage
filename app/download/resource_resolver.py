from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resource import Resource
from app.models.telegram import TelegramSource


@dataclass(frozen=True)
class ResourceLocation:
    resource_id: int
    backend: str
    metadata: dict[str, object] = field(default_factory=dict)
    size: int = 0
    filename: str = ""
    mime_type: str = "application/octet-stream"


class ResourceResolver:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def resolve(self, resource_id: int) -> ResourceLocation:
        resource = await self.session.get(Resource, resource_id)
        if resource is None:
            raise LookupError("resource not found")
        if resource.status != "active":
            raise PermissionError("resource is not available")
        if resource.telegram_message_id is None or resource.source_id is None:
            raise LookupError("resource backend mapping not found")

        source = await self.session.get(TelegramSource, resource.source_id)
        if source is None:
            raise LookupError("resource source not found")
        if not source.enabled:
            raise PermissionError("resource source is disabled")

        return ResourceLocation(
            resource_id=resource.id,
            backend="telegram",
            metadata={
                "chat_id": source.chat_id,
                "message_id": resource.telegram_message_id,
                "account_id": source.account_id,
            },
            size=resource.size,
            filename=resource.filename,
            mime_type=resource.mime_type or "application/octet-stream",
        )

    async def resolve_telegram(self, resource_id: int) -> ResourceLocation:
        return await self.resolve(resource_id)
