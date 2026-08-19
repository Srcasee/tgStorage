from app.indexer.service import is_indexable_message
from app.models.telegram import TelegramSource


class File:
    name = "example.zip"
    mime_type = "application/zip"
    size = 123


class Message:
    id = 1
    media = object()
    file = File()
    deleted = False


def test_indexer_rejects_empty_message():
    assert not is_indexable_message(None)


def test_indexer_rejects_message_without_media():
    message = Message()
    message.media = None
    assert not is_indexable_message(message)


def test_indexer_rejects_message_without_file():
    message = Message()
    message.file = None
    assert not is_indexable_message(message)


def test_indexer_rejects_deleted_message():
    message = Message()
    message.deleted = True
    assert not is_indexable_message(message)


def test_indexer_accepts_live_file_message():
    assert is_indexable_message(Message())


def test_telegram_source_identity_is_account_and_chat_id_not_title():
    index = TelegramSource.__table__.indexes
    unique_indexes = {
        item.name: tuple(column.name for column in item.columns)
        for item in index
        if item.unique
    }
    assert unique_indexes["uq_telegram_sources_account_chat"] == (
        "account_id",
        "chat_id",
    )
