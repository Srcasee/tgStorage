"""Initial tgStorage schema.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-08-20
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "telegram_accounts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=False, unique=True),
        sa.Column("session_path", sa.String(length=512), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="unknown"),
        sa.Column("last_login", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "telegram_sources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("chat_id", sa.BigInteger(), nullable=False),
        sa.Column("chat_type", sa.String(length=32), nullable=False, server_default="channel"),
        sa.Column("title", sa.String(length=256), nullable=False, server_default=""),
        sa.Column("sync_mode", sa.String(length=32), nullable=False, server_default="incremental"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_telegram_sources_account_id", "telegram_sources", ["account_id"])
    op.create_index("ix_telegram_sources_chat_id", "telegram_sources", ["chat_id"])

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_categories_parent_id", "categories", ["parent_id"])

    op.create_table(
        "network_plugins",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column("config_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="unknown"),
    )

    op.create_table(
        "resources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("telegram_message_id", sa.BigInteger(), nullable=True),
        sa.Column("filename", sa.String(length=512), nullable=False, server_default=""),
        sa.Column("extension", sa.String(length=32), nullable=False, server_default=""),
        sa.Column("mime_type", sa.String(length=128), nullable=False, server_default=""),
        sa.Column("resource_type", sa.String(length=32), nullable=False, server_default="unknown"),
        sa.Column("tags_json", sa.JSON(), nullable=True),
        sa.Column("size", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("hash", sa.String(length=128), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
    )
    op.create_index("ix_resources_source_message", "resources", ["source_id", "telegram_message_id"], unique=True)
    op.create_index("ix_resources_category_id", "resources", ["category_id"])
    op.create_index("ix_resources_status", "resources", ["status"])
    op.create_index("ix_resources_resource_type", "resources", ["resource_type"])
    op.create_index("ix_resources_filename", "resources", ["filename"])


def downgrade() -> None:
    op.drop_index("ix_resources_filename", table_name="resources")
    op.drop_index("ix_resources_resource_type", table_name="resources")
    op.drop_index("ix_resources_status", table_name="resources")
    op.drop_index("ix_resources_category_id", table_name="resources")
    op.drop_index("ix_resources_source_message", table_name="resources")
    op.drop_table("resources")
    op.drop_table("network_plugins")
    op.drop_index("ix_categories_parent_id", table_name="categories")
    op.drop_table("categories")
    op.drop_index("ix_telegram_sources_chat_id", table_name="telegram_sources")
    op.drop_index("ix_telegram_sources_account_id", table_name="telegram_sources")
    op.drop_table("telegram_sources")
    op.drop_table("telegram_accounts")
