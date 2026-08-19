"""Storage backend abstraction."""

from abc import ABC, abstractmethod


class StorageBackend(ABC):
    """Common interface for storage providers."""

    @abstractmethod
    async def get_file_info(self, resource_id: int):
        raise NotImplementedError

    @abstractmethod
    async def stream(self, resource_id: int, offset: int = 0):
        raise NotImplementedError
