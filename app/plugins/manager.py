from __future__ import annotations

from app.plugins.base import Plugin


class PluginManager:
    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}

    def register(self, plugin: Plugin) -> None:
        self._plugins[plugin.name] = plugin

    def get(self, name: str) -> Plugin | None:
        return self._plugins.get(name)

    async def startup(self) -> None:
        for plugin in self._plugins.values():
            await plugin.startup()

    async def shutdown(self) -> None:
        for plugin in self._plugins.values():
            await plugin.shutdown()
