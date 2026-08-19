from fastapi import APIRouter

from app.v2.api.download import router as download_router
from app.v2.api.resources import router as resources_router

router = APIRouter(prefix="/api/v2")
router.include_router(download_router)
router.include_router(resources_router, prefix="", tags=["resources"])
