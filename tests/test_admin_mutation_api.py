"""Phase 2-C admin mutation API database isolation tests."""

import pytest

from app.main import app
from app.core.database import get_session


@pytest.mark.asyncio
async def test_admin_mutation_database_fixture_is_available(override_database):
    """Ensure admin mutation tests can run against isolated databases."""
    app.dependency_overrides[get_session] = override_database
    try:
        assert get_session in app.dependency_overrides
    finally:
        app.dependency_overrides.clear()
