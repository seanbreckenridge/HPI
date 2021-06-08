from typing import Any

from more_itertools import ilen

from my.window_watcher import history


def unknown(e: Any) -> bool:
    return e.application == "unknown" and e.window_title == "unknown"


def test_window_watcher():
    items = list(history())
    assert len(items) > 5
    # make sure there are no "unknown" items
    assert ilen(filter(unknown, items)) == 0
