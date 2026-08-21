"""HTTP proxy network provider placeholder.

Kept separate so network implementations remain hot-swappable.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HttpProxyNetworkPlugin:
    host: str
    port: int
    enabled: bool = True
    type: str = "http"

    def client_options(self) -> dict:
        if not self.enabled:
            return {}
        return {
            "proxy": (self.host, self.port),
        }
