"""Uniquely identify a Telegram source by account and chat.

Revision ID: 0002_unique_telegram_source_identity
Revises: 0001_initial_schema
Create Date: 2026-08-20
"""

from alembic import op

revision = "0002_unique_telegram_source_identity"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "uq_telegram_sources_account_chat",
        "telegram_sources",
        ["account_id", "chat_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "uq_telegram_sources_account_chat",
        table_name="telegram_sources",
    )
