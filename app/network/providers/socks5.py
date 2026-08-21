"""SOCKS5 network provider."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Socks5NetworkPlugin:
    """Build Telethon-compatible SOCKS5 options."""

    host: str
    port: int
    enabled: bool = True
    type: str = "socks5"

    def client_options(self) -> dict:
        if not self.enabled:
            return {}
        return {
            "proxy": (self.host, self.port),
        }
