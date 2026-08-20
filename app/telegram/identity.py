"""Telegram chat identity normalization helpers."""


def normalize_chat_id(value: int) -> int:
    """Normalize Telethon channel ids to Telegram Bot API style ids.

    Telegram channels are commonly represented by Telethon without the -100
    prefix in some entity flows. Database bindings use the canonical -100 form.
    """
    value = int(value)
    if value > 0:
        return int(f"-100{value}")
    return value
