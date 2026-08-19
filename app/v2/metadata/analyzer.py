"""
Lightweight Resource Analyzer for tgStorage v2.

Responsibilities:
- infer basic file metadata
- detect resource type
- extract simple tags from filenames

This module intentionally avoids heavy dependencies.
"""

from pathlib import Path
import re


VIDEO_EXTENSIONS = {
    "mp4",
    "mkv",
    "avi",
    "mov",
    "webm",
}

IMAGE_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp",
    "gif",
}

DOCUMENT_EXTENSIONS = {
    "pdf",
    "doc",
    "docx",
    "txt",
    "epub",
}


class ResourceAnalyzer:
    """Analyze Telegram resources without external services."""

    def analyze(self, filename: str, mime_type: str | None = None):
        extension = Path(filename).suffix.lower().lstrip(".")

        resource_type = self.detect_type(extension, mime_type)
        tags = self.extract_tags(filename)

        return {
            "extension": extension,
            "resource_type": resource_type,
            "tags": tags,
        }

    def detect_type(self, extension: str, mime_type: str | None = None):
        if mime_type:
            if mime_type.startswith("video/"):
                return "video"
            if mime_type.startswith("image/"):
                return "image"
            if mime_type.startswith("application/"):
                return "document"

        if extension in VIDEO_EXTENSIONS:
            return "video"

        if extension in IMAGE_EXTENSIONS:
            return "image"

        if extension in DOCUMENT_EXTENSIONS:
            return "document"

        return "unknown"

    def extract_tags(self, filename: str):
        stem = Path(filename).stem

        tokens = re.split(r"[\s._\-\[\]()]+", stem)

        ignored = {
            "www",
            "com",
            "mkv",
            "mp4",
        }

        return [
            token
            for token in tokens
            if token
            and token.lower() not in ignored
            and len(token) > 1
        ]
