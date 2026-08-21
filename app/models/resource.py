"""Resource metadata ORM model for tgStorage v2."""

from sqlalchemy import BigInteger, ForeignKey, Index, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Resource(Base):
    __tablename__ = "resources"
    __table_args__ = (
        Index(
            "uq_resources_source_chat_message",
            "source_id",
            "telegram_chat_id",
            "telegram_message_id",
            unique=True,
        ),
        Index("ix_resources_telegram_chat_id", "telegram_chat_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[int | None] = mapped_column(
        ForeignKey("telegram_sources.id", ondelete="SET NULL"),
        nullable=True,
    )

    telegram_chat_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    telegram_message_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    filename: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    extension: Mapped[str] = mapped_column(String(32), default="")
    mime_type: Mapped[str] = mapped_column(String(128), default="")
    resource_type: Mapped[str] = mapped_column(String(32), default="unknown")
    tags_json: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    size: Mapped[int] = mapped_column(BigInteger, default=0)
    hash: Mapped[str | None] = mapped_column(String(128), nullable=True)

    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(String(32), default="active")

    source = relationship("TelegramSource", back_populates="resources")
    category = relationship("Category", back_populates="resources")
