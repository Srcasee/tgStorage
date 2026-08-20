from __future__ import annotations

import asyncio
import os
import sys

from telethon import TelegramClient
from sqlalchemy import create_engine, text


async def main() -> None:
    account_name = os.getenv("TG_ACCOUNT_NAME") or (sys.argv[1] if len(sys.argv) > 1 else None)
    if not account_name:
        raise SystemExit("usage: TG_ACCOUNT_NAME=<name> python scripts/list-account-dialogs.py")

    db_url = os.getenv("DATABASE_URL", "sqlite:///./data/files.db")
    engine = create_engine(db_url.replace("sqlite+aiosqlite", "sqlite"))

    with engine.connect() as conn:
        row = conn.execute(
            text("select name, session_path from telegram_accounts where name=:name and enabled=1"),
            {"name": account_name},
        ).fetchone()

    if row is None:
        raise SystemExit(f"telegram account not found: {account_name}")

    api_id = int(os.environ["TG_API_ID"])
    api_hash = os.environ["TG_API_HASH"]

    proxy = None
    if os.getenv("ENABLE_PROXY", "false").lower() == "true":
        proxy = (
            os.getenv("PROXY_TYPE", "socks5"),
            os.getenv("PROXY_HOST", "proxy"),
            int(os.getenv("PROXY_PORT", "1080")),
            True,
        )

    client = TelegramClient(row.session_path, api_id, api_hash, proxy=proxy)
    await client.connect()

    if not await client.is_user_authorized():
        raise SystemExit(f"telegram account unauthorized: {account_name}")

    print(f"===== {row.name} dialogs =====")
    async for dialog in client.iter_dialogs():
        print(f"{dialog.id}\t{dialog.name}\t{type(dialog.entity).__name__}")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
