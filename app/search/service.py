"""Lightweight resource search service for tgStorage v2."""

from sqlalchemy import or_, select

from app.v2.models.resource import Resource


class ResourceSearchService:
    """Search indexed resources without external search engines."""

    def __init__(self, session):
        self.session = session

    async def search(
        self,
        query: str | None = None,
        category_id: int | None = None,
        resource_type: str | None = None,
        limit: int = 50,
    ):
        stmt = select(Resource)

        if query:
            keyword = f"%{query}%"
            stmt = stmt.where(
                or_(
                    Resource.filename.ilike(keyword),
                    Resource.extension.ilike(keyword),
                )
            )

        if category_id:
            stmt = stmt.where(Resource.category_id == category_id)

        if resource_type:
            stmt = stmt.where(Resource.resource_type == resource_type)

        stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
