"""Add per-source Telegram scan cursor.

Revision ID: 0003_scanner_cursor
Revises: 0002_unique_telegram_source_identity
Create Date: 2026-08-20
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_scanner_cursor"
down_revision = "0002_unique_telegram_source_identity"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "telegram_sources",
        sa.Column(
            "last_scanned_message_id",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
    )


def downgrade() -> None:
    op.drop_column("telegram_sources", "last_scanned_message_id")
