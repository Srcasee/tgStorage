#!/usr/bin/env python3
"""Database migration helper.

Alembic is the single source of truth for tgStorage schema.
Use this script instead of creating tables manually.
"""

import subprocess
import sys


def main() -> int:
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        check=False,
    )
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
