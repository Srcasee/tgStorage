"""add resource foreign key relations

Revision ID: 20260821_0001
Revises:
Create Date: 2026-08-21
"""

from alembic import op
import sqlalchemy as sa

revision = "20260821_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # These constraints formalize the existing SQLAlchemy model relationships.
    # Deployment databases should run this after validating existing IDs.
    op.create_foreign_key(
        "fk_resources_source_id",
        "resources",
        "telegram_sources",
        ["source_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_resources_category_id",
        "resources",
        "categories",
        ["category_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade():
    op.drop_constraint("fk_resources_category_id", "resources", type_="foreignkey")
    op.drop_constraint("fk_resources_source_id", "resources", type_="foreignkey")
