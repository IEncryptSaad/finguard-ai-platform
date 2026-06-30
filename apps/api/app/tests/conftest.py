import pytest


@pytest.fixture(autouse=True)
def clear_rate_limit_buckets():
    from app.middleware.rate_limit import _BUCKETS

    _BUCKETS.clear()
    yield
    _BUCKETS.clear()
