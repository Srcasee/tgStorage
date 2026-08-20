import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.api.router import router as api_router
from app.core.config import settings
from app.core.database import engine
from app.indexer.worker import TelegramIndexWorker
from app.models import Base
from app.telegram.lifecycle import create_runtime_lifecycle

app = FastAPI()
app.include_router(api_router)

runtime_lifecycle = create_runtime_lifecycle()
index_worker = TelegramIndexWorker(
    interval=int(os.getenv("INDEX_INTERVAL", "300")),
    batch_size=int(os.getenv("INDEX_BATCH_SIZE", "200")),
)
index_worker_enabled = settings.telegram_api_id is not None and bool(settings.telegram_api_hash)
WEB_INDEX = Path(__file__).resolve().parent / "web" / "index.html"


@app.get("/")
async def home():
    return FileResponse(WEB_INDEX)


@app.get("/web")
async def web():
    return FileResponse(WEB_INDEX)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await runtime_lifecycle.startup()
    if index_worker_enabled:
        index_worker.start()
    else:
        print(
            "[INDEX] Telegram API credentials are not configured; scanner disabled",
            flush=True,
        )


@app.on_event("shutdown")
async def shutdown():
    if index_worker_enabled:
        await index_worker.stop()
    await runtime_lifecycle.shutdown()
