import os
import asyncio
from datetime import datetime, timezone

from telethon import TelegramClient
from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.account import TelegramAccount


TG_API_ID = int(os.getenv("TG_API_ID"))
TG_API_HASH = os.getenv("TG_API_HASH")
TG_PHONE = os.getenv("TG_PHONE")

ACCOUNT_NAME = os.getenv(
    "TG_ACCOUNT_NAME",
    os.getenv("ACCOUNT_NAME", "default")
)

TG_SESSION = os.getenv(
    "TG_SESSION",
    "/data/accounts/default"
)

# Session paths are stored in the container-mounted namespace so they remain
# valid after container recreation and across new deployments.
if TG_SESSION.startswith("./data/"):
    TG_SESSION = TG_SESSION.replace("./data", "/data", 1)

TG_SESSION = os.path.abspath(TG_SESSION)


ENABLE_PROXY = (
    os.getenv("ENABLE_PROXY", "false").lower() == "true"
)

proxy = None

if ENABLE_PROXY:
    proxy = {
        "proxy_type": "socks5",
        "addr": os.getenv("PROXY_HOST", "proxy"),
        "port": int(os.getenv("PROXY_PORT", "1080")),
        "rdns": True
    }
    print("[LOGIN] proxy enabled", flush=True)
else:
    print("[LOGIN] proxy disabled", flush=True)


client = TelegramClient(
    TG_SESSION,
    TG_API_ID,
    TG_API_HASH,
    proxy=proxy
)


async def register_account():
    """注册或更新 Telegram Account，避免重复账号记录。"""
    async with SessionLocal() as session:
        result = await session.execute(
            select(TelegramAccount).where(
                TelegramAccount.name == ACCOUNT_NAME
            )
        )

        account = result.scalar_one_or_none()
        now = datetime.now(timezone.utc)

        if account:
            account.session_path = TG_SESSION
            account.status = "online"
            account.last_login = now
            print("账号已更新:", ACCOUNT_NAME, flush=True)
        else:
            account = TelegramAccount(
                name=ACCOUNT_NAME,
                session_path=TG_SESSION,
                enabled=True,
                status="online",
                last_login=now,
            )
            session.add(account)
            print("账号已注册:", ACCOUNT_NAME, flush=True)

        await session.commit()


async def main():
    print("开始登录 Telegram", flush=True)

    await client.start(phone=TG_PHONE)

    me = await client.get_me()

    print(
        "登录成功:",
        me.username or me.first_name,
        flush=True
    )

    await register_account()

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
