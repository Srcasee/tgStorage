import os
import asyncio

from telethon import TelegramClient


# =====================================================
# 环境变量
# =====================================================

TG_API_ID = int(
    os.getenv("TG_API_ID")
)

TG_API_HASH = os.getenv(
    "TG_API_HASH"
)

TG_PHONE = os.getenv(
    "TG_PHONE"
)


TG_SESSION = os.getenv(
    "TG_SESSION",
    "/data/accounts/default"
)

TG_SESSION = os.path.abspath(TG_SESSION)



# =====================================================
# 代理配置
# =====================================================

ENABLE_PROXY = (
    os.getenv(
        "ENABLE_PROXY",
        "false"
    ).lower()
    == "true"
)


proxy = None


if ENABLE_PROXY:

    proxy = {
        "proxy_type": "socks5",
        "addr": os.getenv(
            "PROXY_HOST",
            "proxy"
        ),
        "port": int(
            os.getenv(
                "PROXY_PORT",
                "1080"
            )
        ),
        "rdns": True
    }


    print(
        "[LOGIN] proxy enabled",
        flush=True
    )


else:

    print(
        "[LOGIN] proxy disabled",
        flush=True
    )


# =====================================================
# 登录
# =====================================================

client = TelegramClient(
    TG_SESSION,
    TG_API_ID,
    TG_API_HASH,
    proxy=proxy
)


async def main():

    print(
        "开始登录 Telegram",
        flush=True
    )


    await client.start(
        phone=TG_PHONE
    )


    me = await client.get_me()


    print(
        "登录成功:",
        me.username or me.first_name,
        flush=True
    )


    await client.disconnect()



if __name__ == "__main__":
    asyncio.run(main())