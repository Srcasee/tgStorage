from __future__ import annotations

from abc import ABC


class Plugin(ABC):
    name: str = "plugin"

    async def startup(self) -> None:
        return None

    async def shutdown(self) -> None:
        return None
