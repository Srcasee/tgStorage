"""tgStorage v2 core configuration placeholder.

Phase 0 keeps configuration isolated from legacy modules.
"""

from dataclasses import dataclass


@dataclass
class Settings:
    app_name: str = "tgStorage"
    version: str = "2.0"


settings = Settings()
