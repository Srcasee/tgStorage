from dataclasses import dataclass
from typing import AsyncIterator, Optional


@dataclass
class StreamMetadata:
    size: int
    content_type: str = "application/octet-stream"
    filename: Optional[str] = None


class RangeStreamBuilder:
    """Build streaming metadata for HTTP range responses.

    This layer intentionally does not depend on Telegram or storage backends.
    It receives byte chunks from download engines and exposes HTTP response
    metadata required by browsers and media players.
    """

    def headers(self, metadata: StreamMetadata, start: int = 0, end: int | None = None):
        final_end = metadata.size - 1 if end is None else end
        return {
            "Accept-Ranges": "bytes",
            "Content-Length": str(final_end - start + 1),
            "Content-Range": f"bytes {start}-{final_end}/{metadata.size}",
            "Content-Type": metadata.content_type,
        }

    async def stream(self, chunks: AsyncIterator[bytes]):
        async for chunk in chunks:
            yield chunk
