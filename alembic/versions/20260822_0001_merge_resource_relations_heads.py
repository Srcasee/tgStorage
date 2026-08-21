"""merge alembic heads

Revision ID: 20260822_0001
Revises: 0004_domain_resource_identity, 20260821_0001
Create Date: 2026-08-22

This migration contains no schema operations. It only merges two existing
Alembic branches so deployments can continue using `alembic upgrade head`.
"""

revision = "20260822_0001"
down_revision = ("0004_domain_resource_identity", "20260821_0001")
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
