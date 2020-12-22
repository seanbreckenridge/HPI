from typing import List, Any

from more_itertools import ilen

from my.window_watcher import history, Entry


def unknown(e: Any) -> bool:
    return e.application == "unknown" and e.window_title == "unknown"


def test_window_watcher():
    items: List[Entry] = list(history())
    assert len(items) > 5
    assert isinstance(items[0], Entry)
    # make sure there are no "unknown" items
    assert ilen(filter(unknown, items)) == 0
