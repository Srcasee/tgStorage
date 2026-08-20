import os

import pytest
from httpx import AsyncClient


@pytest.fixture
def test_database_url(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    url = f"sqlite+aiosqlite:///{db_file}"
    monkeypatch.setenv("DATABASE_URL", url)
    return url
