from __future__ import annotations

import pytest


class FakeStorageBackend:
    def __init__(self, payload: bytes):
        self.payload = payload

    async def stream(self, start: int = 0, limit: int | None = None):
        data = self.payload[start:]
        if limit is not None:
            data = data[:limit]
        yield data


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
