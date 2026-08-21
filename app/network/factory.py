"""Factory for creating network plugins from configuration records."""

from __future__ import annotations

from typing import Any

from app.network.plugin import DirectNetworkPlugin, NetworkPlugin
from app.network.providers.http import HttpProxyNetworkPlugin
from app.network.providers.socks5 import Socks5NetworkPlugin


class NetworkPluginFactory:
    """Create enabled network providers without coupling runtime to implementations."""

    @staticmethod
    def create(plugin_type: str | None, config: dict[str, Any] | None = None) -> NetworkPlugin:
        config = config or {}
        plugin_type = plugin_type or "direct"

        if plugin_type == "socks5":
            return Socks5NetworkPlugin(
                host=str(config.get("host", "")),
                port=int(config.get("port", 0)),
                enabled=bool(config.get("enabled", True)),
            )

        if plugin_type == "http":
            return HttpProxyNetworkPlugin(
                host=str(config.get("host", "")),
                port=int(config.get("port", 0)),
                enabled=bool(config.get("enabled", True)),
            )

        return DirectNetworkPlugin(enabled=bool(config.get("enabled", True)))
