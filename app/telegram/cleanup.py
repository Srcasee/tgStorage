"""Telegram resource cleanup and reconciliation helpers.

The scanner treats chat_id as the Telegram source identity. This module
repairs historical pollution caused by old title/dialog based discovery.
"""

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resource import Resource
from app.models.telegram import TelegramSource


class TelegramResourceCleanup:
    """Validate persisted resources against configured Telegram sources."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def invalidate_out_of_boundary_resources(self) -> int:
        """Mark resources that cannot belong to their current source."""
        result = await self.session.execute(
            select(Resource, TelegramSource)
            .join(TelegramSource, Resource.source_id == TelegramSource.id)
        )

        changed = 0
        for resource, source in result.all():
            if (
                resource.telegram_chat_id is not None
                and int(resource.telegram_chat_id) != int(source.chat_id)
            ):
                if resource.status != "unavailable":
                    resource.status = "unavailable"
                    changed += 1

        await self.session.flush()
        return changed

    async def remove_duplicate_resources(self) -> int:
        """Disable duplicate Telegram message identities, keeping first row."""
        result = await self.session.execute(
            select(Resource).where(Resource.status == "active").order_by(Resource.id)
        )

        seen = set()
        changed = 0
        for resource in result.scalars():
            key = (
                resource.source_id,
                resource.telegram_chat_id,
                resource.telegram_message_id,
            )
            if key in seen:
                resource.status = "duplicate"
                changed += 1
            else:
                seen.add(key)

        await self.session.flush()
        return changed

    async def reconcile(self) -> int:
        changed = await self.invalidate_out_of_boundary_resources()
        changed += await self.remove_duplicate_resources()
        await self.session.commit()
        return changed
