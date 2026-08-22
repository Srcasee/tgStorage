from __future__ import annotations

from app.plugins.base import Plugin


class ProxyPlugin(Plugin):
    name = "proxy"

    def __init__(self, enabled: bool = False) -> None:
        self.enabled = enabled

    def proxy_url(self) -> str | None:
        return None
