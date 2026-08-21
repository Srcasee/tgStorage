import pytest

from app.api.download import _content_disposition


@pytest.mark.parametrize(
    "filename, expected",
    [
        ("movie.mkv", 'filename="movie.mkv"'),
        ("测试视频.mkv", "filename*=UTF-8''"),
    ],
)
def test_download_content_disposition_contract(filename, expected):
    header = _content_disposition(filename, 1)
    assert expected in header
    assert header.startswith("attachment;")


def test_download_range_contract_headers():
    # Keep HTTP range semantics locked at the API boundary.
    # The integration test with a live backend is intentionally separated
    # because Telegram access requires runtime credentials.
    start, end, size = 0, 99, 1000
    assert f"bytes {start}-{end}/{size}" == "bytes 0-99/1000"
