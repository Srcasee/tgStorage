"""Lightweight resource search service for tgStorage."""

from sqlalchemy import or_, select

from app.models.resource import Resource


class ResourceSearchService:
    """Search resources that are currently visible to normal users."""

    def __init__(self, session):
        self.session = session

    async def search(self, query=None, category_id=None, resource_type=None, limit=50):
        limit = max(1, min(int(limit), 100))
        stmt = select(Resource).where(Resource.status == "active")
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
        result = await self.session.execute(stmt.order_by(Resource.id.desc()).limit(limit))
        return list(result.scalars().all())
