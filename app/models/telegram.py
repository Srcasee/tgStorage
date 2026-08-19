"""Telegram source ORM model."""

from sqlalchemy import BigInteger, Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class TelegramSource(Base):
    __tablename__ = "telegram_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(Integer, nullable=False)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    chat_type: Mapped[str] = mapped_column(String(32), default="channel")
    title: Mapped[str] = mapped_column(String(256), default="")
    sync_mode: Mapped[str] = mapped_column(String(32), default="incremental")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    # Incremental cursor scoped to this exact source identity.
    last_scanned_message_id: Mapped[int] = mapped_column(BigInteger, default=0)
