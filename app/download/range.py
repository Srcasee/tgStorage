"""HTTP Range helper utilities for v2 downloads."""

from dataclasses import dataclass


@dataclass
class ByteRange:
    start: int
    end: int | None = None


class RangeParser:
    """Parse simple HTTP Range headers."""

    def parse(self, header: str) -> ByteRange | None:
        if not header or not header.startswith("bytes="):
            return None

        value = header.removeprefix("bytes=")
        start, _, end = value.partition("-")

        if not start.isdigit():
            return None

        return ByteRange(
            start=int(start),
            end=int(end) if end.isdigit() else None,
        )
