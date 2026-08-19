"""Network plugin interface.

Proxy implementations will be added as plugins.
"""

from abc import ABC, abstractmethod


class NetworkPlugin(ABC):
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def health_check(self) -> bool:
        raise NotImplementedError
