import pytest
from fastapi import HTTPException

from app.api.download import _parse_range


def test_parse_range_full_response():
    assert _parse_range(None, 1000) is None


def test_parse_range_explicit_range():
    assert _parse_range("bytes=100-199", 1000) == (100, 199)


def test_parse_range_open_ended_range():
    assert _parse_range("bytes=100-", 1000) == (100, 999)


def test_parse_range_suffix_range():
    assert _parse_range("bytes=-100", 1000) == (900, 999)


def test_parse_range_clamps_end_to_resource_size():
    assert _parse_range("bytes=900-1200", 1000) == (900, 999)


@pytest.mark.parametrize(
    "value",
    [
        "bytes=100-99",
        "bytes=1000-",
        "bytes=abc-def",
        "bytes=100-200,300-400",
        "items=100-200",
        "bytes=-0",
    ],
)
def test_parse_range_rejects_unsatisfiable_or_invalid_ranges(value):
    with pytest.raises(HTTPException) as exc_info:
        _parse_range(value, 1000)
    assert exc_info.value.status_code == 416
