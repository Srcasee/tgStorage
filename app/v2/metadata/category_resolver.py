"""Category resolver for tgStorage v2.

Maps classifier output names to database category ids.
Keeps category handling lightweight without introducing a rule table.
"""

from sqlalchemy import select

from app.v2.models.category import Category


class CategoryResolver:
    def __init__(self, session):
        self.session = session

    async def resolve(self, name: str | None) -> int | None:
        if not name:
            return None

        category = await self.session.scalar(
            select(Category).where(Category.name == name)
        )

        if category:
            return category.id

        category = Category(
            name=name,
            sort_order=0,
        )
        self.session.add(category)
        await self.session.flush()

        return category.id
