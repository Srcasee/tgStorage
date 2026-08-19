from fastapi import APIRouter

from app.v2.api.download import router as download_router

router = APIRouter(prefix="/api/v2")
router.include_router(download_router)
