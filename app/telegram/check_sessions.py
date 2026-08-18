import asyncio
import os

from telethon import TelegramClient

from config import settings, proxy


async def check(name):

    path = f"/data/accounts/{name}"

    client = TelegramClient(
        path,
        settings.TG_API_ID,
        settings.TG_API_HASH,
        proxy=proxy
    )

    await client.connect()

    authorized = await client.is_user_authorized()

    print(
        name,
        "authorized:",
        authorized
    )

    if authorized:

        me = await client.get_me()

        print(
            " id:",
            me.id,
            "username:",
            me.username,
            "name:",
            me.first_name
        )

    await client.disconnect()



async def main():

    for s in [
        "larsniel",
        "test_session"
    ]:
        await check(s)



asyncio.run(main())