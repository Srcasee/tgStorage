from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session
from app.search.service import ResourceSearchService

router = APIRouter(prefix="/resources", tags=["resources"])


async def get_search_service(
    session: AsyncSession = Depends(get_db_session),
) -> ResourceSearchService:
    return ResourceSearchService(session)


@router.get("/search")
async def search_resources(
    q: str | None = Query(default=None),
    category_id: int | None = Query(default=None),
    resource_type: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    service: ResourceSearchService = Depends(get_search_service),
):
    resources = await service.search(
        query=q,
        category_id=category_id,
        resource_type=resource_type,
        limit=limit,
    )

    return [
        {
            "id": item.id,
            "filename": item.filename,
            "extension": item.extension,
            "resource_type": item.resource_type,
            "category_id": item.category_id,
            "tags": item.tags_json,
            "size": item.size,
            "mime_type": item.mime_type,
        }
        for item in resources
    ]
