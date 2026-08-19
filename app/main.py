import os
import asyncio

from fastapi import FastAPI
from fastapi.responses import FileResponse

from files.api import router as files_router
from telegram.client import get_clients
from telegram.scanner import scanner_loop
from database import get_connection

from app.v2.api.router import router as v2_router
from app.v2.telegram.lifecycle import create_runtime_lifecycle

TG_API_ID = int(os.getenv("TG_API_ID", "0"))
TG_API_HASH = os.getenv("TG_API_HASH")

app = FastAPI()
app.include_router(files_router)
app.include_router(v2_router)

v2_runtime_lifecycle = create_runtime_lifecycle()
scanner_task = None


@app.get("/")
async def home():
    return FileResponse("/app/web/index.html")


@app.get("/web")
async def web():
    return FileResponse("/app/web/index.html")


@app.on_event("startup")
async def startup():
    global scanner_task

    await v2_runtime_lifecycle.startup()

    # Keep the legacy scanner optional. v2 API startup must not depend on
    # legacy sessions being present.
    clients = get_clients()
    if not clients:
        scanner_task = None
        return

    for name, tg_client in clients.items():
        await tg_client.connect()
        authorized = await tg_client.is_user_authorized()
        if not authorized:
            await tg_client.disconnect()

    async def run_scanners():
        tasks = []
        for name, tg_client in clients.items():
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM accounts WHERE session=?",
                (name,),
            )
            row = cursor.fetchone()
            conn.close()

            if not row or not tg_client.is_connected():
                continue
            if not await tg_client.is_user_authorized():
                continue

            async def run_one(account_id, account_name, account_client):
                try:
                    await scanner_loop(account_client, account_id)
                except asyncio.CancelledError:
                    raise
                except Exception as exc:
                    print(f"[SCAN] {account_name} crashed: {exc!r}", flush=True)

            tasks.append(asyncio.create_task(run_one(row[0], name, tg_client)))

        if tasks:
            await asyncio.gather(*tasks)

    scanner_task = asyncio.create_task(run_scanners())


@app.on_event("shutdown")
async def shutdown():
    global scanner_task

    if scanner_task:
        scanner_task.cancel()
        try:
            await scanner_task
        except asyncio.CancelledError:
            pass

    for name, tg_client in get_clients().items():
        if tg_client.is_connected():
            await tg_client.disconnect()

    await v2_runtime_lifecycle.shutdown()
