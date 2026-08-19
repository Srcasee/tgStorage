from __future__ import annotations

from typing import Any


class ResourceClassifier:
    """Lightweight rule based category classifier.

    This intentionally avoids external ML/search dependencies. Rules can be
    replaced by an admin-managed source later without changing the scanner.
    """

    def __init__(self, rules: list[dict[str, Any]] | None = None):
        self.rules = rules or self.default_rules()

    @staticmethod
    def default_rules() -> list[dict[str, Any]]:
        return [
            {
                "keywords": ["anime", "1080p", "720p"],
                "category": "动漫",
            },
            {
                "extensions": ["pdf", "doc", "docx", "epub"],
                "category": "文档",
            },
            {
                "types": ["video"],
                "category": "视频",
            },
            {
                "types": ["image"],
                "category": "图片",
            },
        ]

    def classify(
        self,
        filename: str,
        resource_type: str,
        tags: list[str] | None = None,
    ) -> str | None:
        name = filename.lower()
        tag_values = [item.lower() for item in (tags or [])]

        extension = ""
        if "." in filename:
            extension = filename.rsplit(".", 1)[-1].lower()

        for rule in self.rules:
            if any(k.lower() in name or k.lower() in tag_values for k in rule.get("keywords", [])):
                return rule["category"]

            if extension and extension in rule.get("extensions", []):
                return rule["category"]

            if resource_type in rule.get("types", []):
                return rule["category"]

        return None
