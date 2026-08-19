"""Resource API schemas for tgStorage v2."""

from pydantic import BaseModel


class ResourceSearchItem(BaseModel):
    id: int
    filename: str
    extension: str | None = None
    resource_type: str | None = None
    category_id: int | None = None
    tags: list[str] | None = None

    model_config = {
        "from_attributes": True,
    }
