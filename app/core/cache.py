# app/core/cache.py

import time
from collections import OrderedDict
from typing import Any, Optional


class TTLCache:
    """Thread-safe in-memory LRU cache with per-item TTL (seconds)."""

    def __init__(self, maxsize: int = 128, ttl: float = 300.0):
        self._maxsize = maxsize
        self._default_ttl = ttl
        self._data: OrderedDict[str, tuple[float, float, Any]] = OrderedDict()

    def get(self, key: str) -> Any | None:
        item = self._data.get(key)
        if item is None:
            return None
        expires_at, stored_ttl, value = item
        if time.monotonic() > expires_at:
            del self._data[key]
            return None
        self._data.move_to_end(key)
        return value

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        ttl_value = ttl if ttl is not None else self._default_ttl
        self._data[key] = (time.monotonic() + ttl_value, ttl_value, value)
        self._data.move_to_end(key)
        while len(self._data) > self._maxsize:
            self._data.popitem(last=False)

    def __len__(self) -> int:
        return len(self._data)


shared_cache = TTLCache()