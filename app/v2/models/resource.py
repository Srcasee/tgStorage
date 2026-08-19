"""Resource metadata entities for tgStorage v2."""

from dataclasses import dataclass


@dataclass
class Resource:
    id: int | None = None
    source_id: int | None = None
    telegram_message_id: int | None = None
    filename: str = ""
    mime_type: str = ""
    size: int = 0
    category_id: int | None = None
