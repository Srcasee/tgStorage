"""Initial tgStorage v2 schema.

Creates lightweight metadata schema:
- telegram_accounts
- telegram_sources
- resources
- categories
- network_plugins
"""

from alembic import op
import sqlalchemy as sa

revision = "001_initial_v2_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "telegram_accounts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("session_path", sa.String(512), nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default=sa.true()),
        sa.Column("status", sa.String(32)),
        sa.Column("last_login", sa.DateTime()),
    )

    op.create_table(
        "telegram_sources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("chat_id", sa.BigInteger(), nullable=False),
        sa.Column("chat_type", sa.String(32)),
        sa.Column("title", sa.String(256)),
        sa.Column("sync_mode", sa.String(32)),
        sa.Column("enabled", sa.Boolean(), server_default=sa.true()),
        sa.ForeignKeyConstraint(["account_id"], ["telegram_accounts.id"]),
        sa.UniqueConstraint("account_id", "chat_id", name="uq_source_account_chat"),
    )

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("parent_id", sa.Integer()),
        sa.Column("sort_order", sa.Integer(), server_default="0"),
        sa.ForeignKeyConstraint(["parent_id"], ["categories.id"]),
    )

    op.create_table(
        "resources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("telegram_message_id", sa.BigInteger(), nullable=False),
        sa.Column("filename", sa.String(512)),
        sa.Column("extension", sa.String(32)),
        sa.Column("mime_type", sa.String(128)),
        sa.Column("size", sa.BigInteger()),
        sa.Column("hash", sa.String(128)),
        sa.Column("category_id", sa.Integer()),
        sa.Column("status", sa.String(32)),
        sa.ForeignKeyConstraint(["source_id"], ["telegram_sources.id"]),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.UniqueConstraint("source_id", "telegram_message_id", name="uq_resource_message"),
    )

    op.create_index("ix_resources_filename", "resources", ["filename"])
    op.create_index("ix_resources_mime_type", "resources", ["mime_type"])
    op.create_index("ix_resources_source_id", "resources", ["source_id"])
    op.create_index("ix_resources_category_id", "resources", ["category_id"])

    op.create_table(
        "network_plugins",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("type", sa.String(64), nullable=False),
        sa.Column("config_json", sa.Text()),
        sa.Column("enabled", sa.Boolean(), server_default=sa.false()),
        sa.Column("priority", sa.Integer(), server_default="0"),
        sa.Column("status", sa.String(32)),
    )


def downgrade():
    op.drop_index("ix_resources_category_id", table_name="resources")
    op.drop_index("ix_resources_source_id", table_name="resources")
    op.drop_index("ix_resources_mime_type", table_name="resources")
    op.drop_index("ix_resources_filename", table_name="resources")

    for table in [
        "network_plugins",
        "resources",
        "categories",
        "telegram_sources",
        "telegram_accounts",
    ]:
        op.drop_table(table)
