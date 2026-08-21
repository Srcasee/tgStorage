from app.api.download import _content_disposition


def test_content_disposition_contains_safe_ascii_filename():
    header = _content_disposition("movie.mkv", 1)

    assert 'filename="movie.mkv"' in header
    assert "filename*=UTF-8''" in header


def test_content_disposition_supports_utf8_filename():
    header = _content_disposition("测试视频.mkv", 1)

    assert 'filename*=' in header
    assert "%E" in header
