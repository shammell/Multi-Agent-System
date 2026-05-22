import pytest

from src.core.message_bus import ExponentialBackoff


def test_backoff_grows_exponentially_with_cap_and_jitter_bounds():
    b = ExponentialBackoff(base_delay=0.1, max_delay=1.0, jitter=0.2, max_retries=5, rng=lambda: 0.5)
    d1 = b.next_delay(1)
    d2 = b.next_delay(2)
    d3 = b.next_delay(3)
    assert d1 < d2 < d3 <= 1.0


def test_backoff_raises_after_max_retries():
    b = ExponentialBackoff(base_delay=0.1, max_delay=1.0, jitter=0.0, max_retries=2, rng=lambda: 0.0)
    b.next_delay(1)
    b.next_delay(2)
    with pytest.raises(RuntimeError):
        b.next_delay(3)


def test_non_429_should_not_retry():
    b = ExponentialBackoff(base_delay=0.1, max_delay=1.0, jitter=0.0, max_retries=3, rng=lambda: 0.0)
    assert b.should_retry(429) is True
    assert b.should_retry(500) is False
