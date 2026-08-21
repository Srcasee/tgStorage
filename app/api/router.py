from fastapi import APIRouter

from app.api.admin import router as admin_router
from app.api.download import router as download_router
from app.api.resources import router as resources_router

router = APIRouter(prefix="/api/v2")
router.include_router(resources_router)
router.include_router(download_router)
router.include_router(admin_router)
