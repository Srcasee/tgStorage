"""Network plugin selection layer for tgStorage v2."""

from __future__ import annotations

from app.network.plugin import DirectNetworkPlugin, NetworkPlugin


class NetworkSelector:
    """Small registry; proxy implementations can be added/removed at runtime."""

    def __init__(self) -> None:
        self._plugins: dict[str, NetworkPlugin] = {}
        self.register(DirectNetworkPlugin())

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
