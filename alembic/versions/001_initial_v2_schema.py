"""Initial tgStorage v2 schema.

Creates core metadata tables:
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
        sa.Column("enabled", sa.Boolean(), default=True),
        sa.Column("status", sa.String(32)),
    )

    op.create_table(
        "telegram_sources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("chat_id", sa.BigInteger(), nullable=False),
        sa.Column("chat_type", sa.String(32)),
        sa.Column("title", sa.String(256)),
        sa.Column("sync_mode", sa.String(32)),
        sa.Column("enabled", sa.Boolean(), default=True),
    )

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("parent_id", sa.Integer()),
        sa.Column("sort_order", sa.Integer()),
    )

    op.create_table(
        "resources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_id", sa.Integer()),
        sa.Column("telegram_message_id", sa.BigInteger()),
        sa.Column("filename", sa.String(512)),
        sa.Column("extension", sa.String(32)),
        sa.Column("mime_type", sa.String(128)),
        sa.Column("size", sa.BigInteger()),
        sa.Column("hash", sa.String(128)),
        sa.Column("category_id", sa.Integer()),
        sa.Column("status", sa.String(32)),
    )

    op.create_table(
        "network_plugins",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(128)),
        sa.Column("type", sa.String(64)),
        sa.Column("config_json", sa.Text()),
        sa.Column("enabled", sa.Boolean()),
        sa.Column("priority", sa.Integer()),
        sa.Column("status", sa.String(32)),
    )


def downgrade():
    for table in [
        "network_plugins",
        "resources",
        "categories",
        "telegram_sources",
        "telegram_accounts",
    ]:
        op.drop_table(table)
