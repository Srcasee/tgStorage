from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.v2.models.resource import Resource
from app.v2.models.telegram import TelegramSource


@dataclass(frozen=True)
class TelegramResourceLocation:
    resource_id: int
    chat_id: int
    message_id: int
    account_id: int | None = None
    size: int = 0
    filename: str = ""
    mime_type: str = "application/octet-stream"


class ResourceResolver:
    """Resolve an indexed resource into its Telegram storage location."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def resolve_telegram(self, resource_id: int) -> TelegramResourceLocation:
        resource = await self.session.get(Resource, resource_id)
        if resource is None:
            raise LookupError("resource not found")
        if resource.telegram_message_id is None or resource.source_id is None:
            raise LookupError("resource has no Telegram message mapping")

        source = await self.session.get(TelegramSource, resource.source_id)
        if source is None:
            raise LookupError("Telegram source not found")
        if not source.enabled:
            raise PermissionError("Telegram source is disabled")

        return TelegramResourceLocation(
            resource_id=resource.id,
            chat_id=source.chat_id,
            message_id=resource.telegram_message_id,
            account_id=source.account_id,
            size=resource.size,
            filename=resource.filename,
            mime_type=resource.mime_type or "application/octet-stream",
        )
