"""Alembic environment for tgStorage v2."""

from app.v2.models import Base

# Alembic uses this metadata for autogeneration.
target_metadata = Base.metadata
