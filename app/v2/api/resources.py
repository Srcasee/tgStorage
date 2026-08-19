"""Resource API endpoints for tgStorage v2."""

from fastapi import APIRouter, Depends, Query

from app.v2.search.service import ResourceSearchService

router = APIRouter(prefix="/api/v2/resources", tags=["resources"])


async def get_search_service():
    """Placeholder dependency, wired to database session in application bootstrap."""
    raise NotImplementedError


@router.get("/search")
async def search_resources(
    q: str | None = Query(default=None),
    category_id: int | None = Query(default=None),
    resource_type: str | None = Query(default=None),
    service: ResourceSearchService = Depends(get_search_service),
):
    resources = await service.search(
        query=q,
        category_id=category_id,
        resource_type=resource_type,
    )

    return [
        {
            "id": item.id,
            "filename": item.filename,
            "extension": item.extension,
            "resource_type": item.resource_type,
            "category_id": item.category_id,
            "tags": item.tags_json,
        }
        for item in resources
    ]
