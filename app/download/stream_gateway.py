from typing import AsyncIterator

from .stream_response import RangeStreamBuilder, StreamMetadata


class StreamGateway:
    """Connect download chunks to HTTP streaming layer."""

    def __init__(self):
        self.response_builder = RangeStreamBuilder()

    async def stream(
        self,
        chunks: AsyncIterator[bytes],
        metadata: StreamMetadata,
        start: int = 0,
        end: int | None = None,
    ):
        return {
            "headers": self.response_builder.headers(metadata, start, end),
            "body": self.response_builder.stream(chunks),
        }
