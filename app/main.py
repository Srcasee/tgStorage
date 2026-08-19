import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.api.router import router as api_router
from app.indexer.worker import TelegramIndexWorker
from app.telegram.lifecycle import create_runtime_lifecycle

app = FastAPI()
app.include_router(api_router)

runtime_lifecycle = create_runtime_lifecycle()
index_worker = TelegramIndexWorker(
    interval=int(os.getenv("INDEX_INTERVAL", "300")),
    batch_size=int(os.getenv("INDEX_BATCH_SIZE", "200")),
)
WEB_INDEX = Path(__file__).resolve().parent / "web" / "index.html"


@app.get("/")
async def home():
    return FileResponse(WEB_INDEX)


@app.get("/web")
async def web():
    return FileResponse(WEB_INDEX)


@app.on_event("startup")
async def startup():
    await runtime_lifecycle.startup()
    index_worker.start()


@app.on_event("shutdown")
async def shutdown():
    await index_worker.stop()
    await runtime_lifecycle.shutdown()
