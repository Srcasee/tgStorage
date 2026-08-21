"""Load enabled network plugins into the runtime selector."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from app.network.factory import NetworkPluginFactory
from app.network.selector import NetworkSelector


DEFAULT_DB_PATH = Path("data/tgstorage.db")


def load_network_plugins(
    selector: NetworkSelector,
    db_path: Path = DEFAULT_DB_PATH,
) -> int:
    """Load enabled network plugins from the local database.

    The loader intentionally uses sqlite directly to match the current lightweight
    runtime database access pattern and avoids introducing a second ORM session
    lifecycle.
    """
    if not db_path.exists():
        return 0

    loaded = 0
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT type, config_json
            FROM network_plugins
            WHERE enabled = 1
            ORDER BY priority DESC
            """
        ).fetchall()

    for row in rows:
        config = json.loads(row["config_json"] or "{}")
        plugin = NetworkPluginFactory.create(row["type"], config)
        selector.register(plugin)
        loaded += 1

    return loaded
