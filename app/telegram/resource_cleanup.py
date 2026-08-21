"""Telegram resource cleanup helpers.

Keeps historical scanner mistakes from leaking resources across Telegram
sources. Resources are never matched by title; only source_id and
telegram_chat_id define ownership.
"""

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resource import Resource
from app.models.telegram import TelegramSource


async def invalidate_resources_outside_source_boundary(
    session: AsyncSession,
    source: TelegramSource,
) -> int:
    """Mark resources not belonging to the current Telegram source as unavailable.

    This is intended for repairing databases created before strict source
    binding existed. A Telegram message id is only meaningful inside its chat.
    """

    result = await session.execute(
        update(Resource)
        .where(Resource.source_id == source.id)
        .where(Resource.telegram_chat_id != source.chat_id)
        .where(Resource.status == "active")
        .values(status="unavailable")
    )

    await session.commit()
    return result.rowcount or 0
