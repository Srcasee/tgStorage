"""Phase 1B download endpoint E2E contract tests.

These tests intentionally keep Telegram out of CI. They validate the HTTP layer
against a fake storage backend contract so StorageBackend implementations remain
replaceable.
"""

from dataclasses import dataclass


@dataclass
class FakeStorageBackend:
    payload: bytes = b"0123456789"

    async def stream(self, start=0, length=None):
        data = self.payload[start:]
        if length is not None:
            data = data[:length]
        yield data


async def test_fake_backend_full_stream():
    backend = FakeStorageBackend()
    chunks = []

    async for chunk in backend.stream():
        chunks.append(chunk)

    assert b"".join(chunks) == b"0123456789"


async def test_fake_backend_range_stream():
    backend = FakeStorageBackend()
    chunks = []

    async for chunk in backend.stream(start=2, length=4):
        chunks.append(chunk)

    assert b"".join(chunks) == b"2345"
