"""Network plugin selection layer for tgStorage v2.

Network/proxy handling stays optional and hot-swappable.
"""

from typing import Any, Optional


class NetworkSelector:
    def __init__(self):
        self._plugins: list[Any] = []

    def register(self, plugin: Any):
        self._plugins.append(plugin)

    def select(self, network_type: Optional[str] = None):
        for plugin in self._plugins:
            if not getattr(plugin, "enabled", True):
                continue
            if network_type is None:
                return plugin
            if getattr(plugin, "type", None) == network_type:
                return plugin
        return None
