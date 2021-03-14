from datetime import timedelta

import pytest

from my.zsh import history
from my.utils.query import find_hpi_function, QueryException, most_recent, order_by_date


def test_query_succeeds():
    assert hasattr(next(find_hpi_function("my.zsh", "history")()), "command")


def test_query_fails():
    with pytest.raises(QueryException):
        find_hpi_function("my.zshh", "history")
    with pytest.raises(QueryException):
        find_hpi_function("my.zsh", "historyy")


def test_get_recent():
    zsh_hist = find_hpi_function("my.zsh", "history")

    recent_events = list(most_recent(zsh_hist(), events=100))
    assert len(recent_events) == 100

    recent_events = list(most_recent(zsh_hist(), events=5))
    assert len(recent_events) == 5

    recent_events = list(most_recent(zsh_hist(), time_range=True))  # default 250
    assert len(recent_events) == 250

    # find most recent zsh history event 'manually'
    manual_most_recent = sorted(history(), key=lambda o: o.dt)[-1]

    # make sure 'most_recent' function returns the right info
    assert int(manual_most_recent.dt.timestamp()) == int(
        recent_events[0].dt.timestamp()
    )


def test_order_by_date():
    zsh_hist = find_hpi_function("my.zsh", "history")
    all_zsh_history = list(zsh_hist())

    # includes default kwargs which reduce this to 250 or within the last month
    recent_items = list(most_recent(zsh_hist()))
    assert len(recent_items) < len(all_zsh_history)

    # make sure order_by_date doesnt remove items for some reason
    all_items_ordered = list(order_by_date(zsh_hist()))
    assert len(all_items_ordered) == len(all_zsh_history)
