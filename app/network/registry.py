"""Process-local network selector registry."""

from __future__ import annotations

from pathlib import Path

from app.network.loader import load_network_plugins
from app.network.selector import NetworkSelector

_selector: NetworkSelector | None = None


def get_network_selector() -> NetworkSelector:
    global _selector
    if _selector is None:
        _selector = NetworkSelector()
    return _selector


def reload_network_selector(db_path: Path | None = None) -> int:
    """Reload enabled network plugins into the shared runtime selector."""
    global _selector

    _selector = NetworkSelector()
    if db_path is None:
        return load_network_plugins(_selector)
    return load_network_plugins(_selector, db_path=db_path)


def reset_network_selector() -> None:
    global _selector
    _selector = None
