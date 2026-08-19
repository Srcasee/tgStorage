"""Make Telegram resource identity explicitly chat-bound.

Revision ID: 0004_domain_resource_identity
Revises: 0003_scanner_cursor
"""

from alembic import op
import sqlalchemy as sa

revision = "0004_domain_resource_identity"
down_revision = "0003_scanner_cursor"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "telegram_sources",
        sa.Column("bound_chat_id", sa.BigInteger(), nullable=True),
    )
    op.execute(
        "UPDATE telegram_sources SET bound_chat_id = chat_id WHERE bound_chat_id IS NULL"
    )

    op.add_column(
        "resources",
        sa.Column("telegram_chat_id", sa.BigInteger(), nullable=True),
    )

    # Existing v2 rows do not contain a trustworthy chat identity. Do not
    # guess it from the current source binding: those rows may have originated
    # from the old dialog-enumerating scanner. Hide them until a source-scoped
    # scan recreates them with an explicit Telegram chat id.
    op.execute(
        "UPDATE resources SET status = 'unavailable' "
        "WHERE telegram_chat_id IS NULL"
    )

    op.drop_index("ix_resources_source_message", table_name="resources")
    op.create_index(
        "uq_resources_source_chat_message",
        "resources",
        ["source_id", "telegram_chat_id", "telegram_message_id"],
        unique=True,
    )
    op.create_index(
        "ix_resources_telegram_chat_id",
        "resources",
        ["telegram_chat_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_resources_telegram_chat_id", table_name="resources")
    op.drop_index("uq_resources_source_chat_message", table_name="resources")
    op.create_index(
        "ix_resources_source_message",
        "resources",
        ["source_id", "telegram_message_id"],
        unique=True,
    )
    op.drop_column("resources", "telegram_chat_id")
    op.drop_column("telegram_sources", "bound_chat_id")
