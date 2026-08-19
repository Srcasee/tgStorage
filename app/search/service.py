"""Lightweight resource search service for tgStorage."""

from sqlalchemy import or_, select

from app.models.resource import Resource


class ResourceSearchService:
    """Search indexed resources without an external search engine."""

    def __init__(self, session):
        self.session = session

    async def search(self, query=None, category_id=None, resource_type=None, limit=50):
        stmt = select(Resource)
        if query:
            keyword = f"%{query}%"
            stmt = stmt.where(or_(Resource.filename.ilike(keyword), Resource.extension.ilike(keyword)))
        if category_id:
            stmt = stmt.where(Resource.category_id == category_id)
        if resource_type:
            stmt = stmt.where(Resource.resource_type == resource_type)
        result = await self.session.execute(stmt.limit(limit))
        return list(result.scalars().all())
