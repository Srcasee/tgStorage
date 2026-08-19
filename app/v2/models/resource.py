"""Resource metadata ORM model for tgStorage v2."""

from sqlalchemy import BigInteger, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    telegram_message_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    filename: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    extension: Mapped[str] = mapped_column(String(32), default="")
    mime_type: Mapped[str] = mapped_column(String(128), default="")
    size: Mapped[int] = mapped_column(BigInteger, default=0)
    hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    category_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active")
