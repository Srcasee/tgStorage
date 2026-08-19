"""Telegram account and source ORM models."""

from sqlalchemy import BigInteger, Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class TelegramAccount(Base):
    __tablename__ = "telegram_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    session_path: Mapped[str] = mapped_column(String(512), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(32), default="unknown")


class TelegramSource(Base):
    __tablename__ = "telegram_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(Integer, nullable=False)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    chat_type: Mapped[str] = mapped_column(String(32), default="channel")
    title: Mapped[str] = mapped_column(String(256), default="")
    sync_mode: Mapped[str] = mapped_column(String(32), default="incremental")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
