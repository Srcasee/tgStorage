"""Minimal hot-swappable network plugin contract."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class NetworkPlugin(Protocol):
    type: str
    enabled: bool

    def client_options(self) -> dict[str, Any]:
        """Return options accepted by the network client, without secrets."""


@dataclass(frozen=True)
class DirectNetworkPlugin:
    type: str = "direct"
    enabled: bool = True

    def client_options(self) -> dict[str, Any]:
        return {}
