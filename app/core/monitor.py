from threading import Lock
from typing import Dict

_lock = Lock()
_counters: Dict[str, int] = {}


def incr(metric: str, amount: int = 1) -> None:
    with _lock:
        _counters[metric] = _counters.get(metric, 0) + amount


def get(metric: str) -> int:
    with _lock:
        return _counters.get(metric, 0)


def reset(metric: str) -> None:
    with _lock:
        _counters[metric] = 0


def all_metrics() -> Dict[str, int]:
    with _lock:
        return dict(_counters)
