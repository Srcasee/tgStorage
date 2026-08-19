"""Resolve storage metadata from indexed resources."""


class ResourceResolver:
    """Convert Resource ORM objects into download backend inputs."""

    def resolve_telegram(self, resource):
        source = getattr(resource, "source", None)
        if source is None:
            raise ValueError("resource source is missing")

        return {
            "chat_id": source.chat_id,
            "message_id": resource.telegram_message_id,
        }
