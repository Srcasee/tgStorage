"""Process-local network selector registry."""

from __future__ import annotations

from app.network.selector import NetworkSelector

_selector: NetworkSelector | None = None


def get_network_selector() -> NetworkSelector:
    global _selector
    if _selector is None:
        _selector = NetworkSelector()
    return _selector


def reset_network_selector() -> None:
    global _selector
    _selector = None
