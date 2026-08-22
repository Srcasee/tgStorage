"""Telegram source ORM model."""

from sqlalchemy import BigInteger, Boolean, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class TelegramSource(Base):
    __tablename__ = "telegram_sources"
    __table_args__ = (
        Index(
            "uq_telegram_sources_account_chat",
            "account_id",
            "chat_id",
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(Integer, nullable=False)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    chat_type: Mapped[str] = mapped_column(String(32), default="channel")
    title: Mapped[str] = mapped_column(String(256), default="")
    sync_mode: Mapped[str] = mapped_column(String(32), default="incremental")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    # Identity the scanner was originally bound to. If an administrator
    # rebinds ``chat_id``, resources from the old chat must not become the
    # resources of the new chat merely because the source row is reused.
    bound_chat_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    # Incremental cursor scoped to this exact source identity.
    last_scanned_message_id: Mapped[int] = mapped_column(BigInteger, default=0)

    resources = relationship("Resource", back_populates="source")
