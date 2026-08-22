"""Network plugin selection layer for tgStorage."""

from __future__ import annotations

from app.core.config import settings
from app.network.plugin import DirectNetworkPlugin, NetworkPlugin
from app.network.providers.socks5 import Socks5NetworkPlugin


class NetworkSelector:
    """Small registry; proxy implementations can be added/removed at runtime."""

    def __init__(self) -> None:
        self._plugins: dict[str, NetworkPlugin] = {}
        self.register(DirectNetworkPlugin())
        self._register_configured_plugins()

    def _register_configured_plugins(self) -> None:
        proxy = settings.proxy
        if proxy.enabled and proxy.host and proxy.port and proxy.proxy_type == "socks5":
            self.register(
                Socks5NetworkPlugin(
                    host=proxy.host,
                    port=proxy.port,
                    enabled=True,
                )
            )

    def register(self, plugin: NetworkPlugin) -> None:
        self._plugins[plugin.type] = plugin

    def unregister(self, network_type: str) -> None:
        if network_type != "direct":
            self._plugins.pop(network_type, None)

    def select(self, network_type: str | None = None) -> NetworkPlugin | None:
        plugin = self._plugins.get(network_type or "direct")
        if plugin is None or not plugin.enabled:
            return None
        return plugin
