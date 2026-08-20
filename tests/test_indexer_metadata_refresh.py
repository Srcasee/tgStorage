from types import SimpleNamespace

from app.indexer.service import refresh_resource_metadata


def test_refresh_resource_metadata_updates_existing_row():
    resource = SimpleNamespace(
        filename="old.mkv",
        extension="mkv",
        mime_type="video/x-matroska",
        resource_type="video",
        tags_json=["old"],
        size=10,
        category_id=1,
        status="unavailable",
    )

    refresh_resource_metadata(
        resource,
        filename="new.mkv",
        extension="mkv",
        mime_type="video/x-matroska",
        resource_type="video",
        tags=["new", "1080p"],
        size=20,
        category_id=2,
    )

    assert resource.filename == "new.mkv"
    assert resource.tags_json == ["new", "1080p"]
    assert resource.size == 20
    assert resource.category_id == 2
    assert resource.status == "active"
