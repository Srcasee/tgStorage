import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.api.router import router as api_router
from app.core.config import settings
from app.core.database import SessionLocal
from app.download.factory import create_download_service
from app.indexer.worker import TelegramIndexWorker
from app.telegram.lifecycle import create_runtime_lifecycle

runtime_lifecycle = create_runtime_lifecycle()
index_worker = TelegramIndexWorker(
    interval=int(os.getenv("INDEX_INTERVAL", "300")),
    batch_size=int(os.getenv("INDEX_BATCH_SIZE", "200")),
)
index_worker_enabled = settings.telegram_api_id is not None and bool(settings.telegram_api_hash)
WEB_INDEX = Path(__file__).resolve().parent / "web" / "index.html"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await runtime_lifecycle.startup()

    async with SessionLocal() as session:
        app.state.download_service = await create_download_service(session)

        if index_worker_enabled:
            index_worker.start()
        else:
            print(
                "[INDEX] Telegram API credentials are not configured; scanner disabled",
                flush=True,
            )

        try:
            yield
        finally:
            if index_worker_enabled:
                await index_worker.stop()

    await runtime_lifecycle.shutdown()


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": settings.app_name,
        "indexer_enabled": index_worker_enabled,
    }


@app.get("/")
async def home():
    return FileResponse(WEB_INDEX)


@app.get("/web")
async def web():
    return FileResponse(WEB_INDEX)
