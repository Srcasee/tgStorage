"""Discover Telegram dialogs for an account and persist channel/group sources."""
from __future__ import annotations

import asyncio
import os
import sys

from telethon import TelegramClient
from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.account import TelegramAccount
from app.models.telegram import TelegramSource


def build_proxy():
    if os.getenv("ENABLE_PROXY", "false").lower() != "true":
        return None
    return {
        "proxy_type": os.getenv("PROXY_TYPE", "socks5"),
        "addr": os.getenv("PROXY_HOST", "proxy"),
        "port": int(os.getenv("PROXY_PORT", "1080")),
        "rdns": True,
    }


async def sync_sources(account_name: str) -> None:
    async with SessionLocal() as session:
        result = await session.execute(
            select(TelegramAccount).where(TelegramAccount.name == account_name)
        )
        account = result.scalar_one_or_none()
        if account is None:
            raise RuntimeError(f"telegram account not found: {account_name}")

        client = TelegramClient(
            account.session_path,
            int(os.environ["TG_API_ID"]),
            os.environ["TG_API_HASH"],
            proxy=build_proxy(),
        )

        await client.start()

        count = 0
        async for dialog in client.iter_dialogs():
            entity = dialog.entity
            if not getattr(entity, "megagroup", False) and not getattr(entity, "broadcast", False):
                continue

            chat_id = dialog.id
            existing = await session.execute(
                select(TelegramSource).where(
                    TelegramSource.account_id == account.id,
                    TelegramSource.chat_id == chat_id,
                )
            )
            source = existing.scalar_one_or_none()

            if source is None:
                session.add(TelegramSource(
                    account_id=account.id,
                    chat_id=chat_id,
                    title=dialog.name or "",
                    chat_type="channel" if getattr(entity, "broadcast", False) else "group",
                    bound_chat_id=chat_id,
                    enabled=True,
                ))
            else:
                source.title = dialog.name or source.title
            count += 1

        await session.commit()
        await client.disconnect()
        print(f"Registered Telegram sources: {count}")


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else os.getenv("TG_ACCOUNT_NAME")
    if not name:
        raise SystemExit("usage: python scripts/sync_telegram_sources.py <account_name>")
    asyncio.run(sync_sources(name))
