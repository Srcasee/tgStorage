from app.cache.message import MessageCache
from app.telegram.account_score import AccountScore
from app.telegram.account_selector import AccountCandidate, AccountSelector


def test_message_cache_roundtrip():
    cache = MessageCache(max_items=2, ttl_seconds=60)
    value = object()

    cache.set((1, 2), value)

    assert cache.get((1, 2)) is value


def test_account_selector_prefers_highest_score():
    selector = AccountSelector()

    selected = selector.select(
        [
            AccountCandidate(account_id=1, score=10),
            AccountCandidate(account_id=2, score=20),
        ]
    )

    assert selected is not None
    assert selected.account_id == 2


def test_account_score_records_failure():
    score = AccountScore()

    score.record_failure()

    assert score.failure_count == 1
