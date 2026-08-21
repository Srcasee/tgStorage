from __future__ import annotations

import pytest


class FakeStorageBackend:
    """Minimal storage contract used to verify API-layer streaming behavior."""

    def __init__(self, payload: bytes):
        self.payload = payload

    async def stream(self, start: int = 0, limit: int | None = None):
        end = None if limit is None else start + limit
        yield self.payload[start:end]


@pytest.mark.asyncio
async def test_fake_storage_backend_full_stream():
    backend = FakeStorageBackend(b"0123456789")

    chunks = []
    async for chunk in backend.stream():
        chunks.append(chunk)

    assert b"".join(chunks) == b"0123456789"


@pytest.mark.asyncio
async def test_fake_storage_backend_range_stream():
    backend = FakeStorageBackend(b"0123456789")

    chunks = []
    async for chunk in backend.stream(start=2, limit=4):
        chunks.append(chunk)

    assert b"".join(chunks) == b"2345"


@pytest.mark.asyncio
async def test_fake_storage_backend_missing_resource_contract():
    backend = FakeStorageBackend(b"")

    chunks = []
    async for chunk in backend.stream():
        chunks.append(chunk)

    assert b"".join(chunks) == b""
