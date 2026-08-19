import asyncio
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.files.api import router as files_router
from app.telegram.client import get_clients
from app.telegram.scanner import scanner_loop
from app.database import get_connection
from app.api.router import router as api_router
from app.indexer.worker import TelegramIndexWorker
from app.telegram.lifecycle import create_runtime_lifecycle

app = FastAPI()
app.include_router(files_router)
app.include_router(api_router)

runtime_lifecycle = create_runtime_lifecycle()
index_worker = TelegramIndexWorker(
    interval=int(os.getenv("INDEX_INTERVAL", os.getenv("V2_INDEX_INTERVAL", "300"))),
    batch_size=int(os.getenv("INDEX_BATCH_SIZE", os.getenv("V2_INDEX_BATCH_SIZE", "200"))),
)
scanner_task = None
WEB_INDEX = Path(__file__).resolve().parent / "web" / "index.html"


@app.get("/")
async def home():
    return FileResponse(WEB_INDEX)


@app.get("/web")
async def web():
    return FileResponse(WEB_INDEX)


@app.on_event("startup")
async def startup():
    global scanner_task
    await runtime_lifecycle.startup()
    index_worker.start()

    clients = get_clients()
    if not clients:
        return

    for tg_client in clients.values():
        await tg_client.connect()
        if not await tg_client.is_user_authorized():
            await tg_client.disconnect()

    async def run_scanners():
        tasks = []
        for name, tg_client in clients.items():
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM accounts WHERE session=?", (name,))
            row = cursor.fetchone()
            conn.close()
            if not row or not tg_client.is_connected() or not await tg_client.is_user_authorized():
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
    await index_worker.stop()
    if scanner_task:
        scanner_task.cancel()
        try:
            await scanner_task
        except asyncio.CancelledError:
            pass
    for tg_client in get_clients().values():
        if tg_client.is_connected():
            await tg_client.disconnect()
    await runtime_lifecycle.shutdown()
