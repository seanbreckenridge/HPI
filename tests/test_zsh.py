import os
from pathlib import Path

from my.zsh import history, Entry

from .common import data

history_file = data("zsh/zsh_history")
overlap_file = data("zsh/overlap_history")


def test_single_file() -> None:
    """
    test that a single zsh parse works and for an entry in the history
    """

    def zsh_small_test():
        yield Path(history_file)

    items = list(history(from_paths=zsh_small_test))
    assert len(items) == 11

    from datetime import datetime, timezone

    # from the test history file, fine to do
    e = Entry(
        dt=datetime(
            year=2020,
            month=7,
            day=14,
            hour=2,
            minute=21,
            second=37,
            tzinfo=timezone.utc,
        ),
        duration=0,
        command="ls",
    )
    assert e in items


def test_overlap() -> None:
    """
    To make sure that duplicates are removed
    """

    def zsh_multiple_tests():
        yield Path(history_file)
        yield Path(overlap_file)

    items = list(history(from_paths=zsh_multiple_tests))
    assert len(items) == 11
