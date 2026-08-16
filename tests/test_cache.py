# tests/test_cache.py

import time

from app.core.cache import TTLCache


def test_set_and_get():
    cache = TTLCache()
    cache.set("a", {"rating": 8})
    assert cache.get("a") == {"rating": 8}


def test_get_missing_returns_none():
    cache = TTLCache()
    assert cache.get("missing") is None


def test_ttl_expiry():
    cache = TTLCache(ttl=0.05)
    cache.set("a", "value")
    assert cache.get("a") == "value"
    time.sleep(0.1)
    assert cache.get("a") is None


def test_custom_ttl_per_item():
    cache = TTLCache(ttl=0.05)
    cache.set("short", "x", ttl=0.05)
    cache.set("long", "y", ttl=100)
    time.sleep(0.1)
    assert cache.get("short") is None
    assert cache.get("long") == "y"


def test_lru_eviction():
    cache = TTLCache(maxsize=2)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("c", 3)
    assert cache.get("a") is None
    assert cache.get("b") == 2
    assert cache.get("c") == 3