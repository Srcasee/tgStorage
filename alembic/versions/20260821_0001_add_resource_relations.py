"""add resource foreign key relations

Revision ID: 20260821_0001
Revises: 0004_domain_resource_identity
Create Date: 2026-08-21
"""

from alembic import op

revision = "20260821_0001"
down_revision = "0004_domain_resource_identity"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("resources") as batch_op:
        batch_op.create_foreign_key(
            "fk_resources_source_id",
            "telegram_sources",
            ["source_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch_op.create_foreign_key(
            "fk_resources_category_id",
            "categories",
            ["category_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade():
    with op.batch_alter_table("resources") as batch_op:
        batch_op.drop_constraint("fk_resources_category_id", type_="foreignkey")
        batch_op.drop_constraint("fk_resources_source_id", type_="foreignkey")
