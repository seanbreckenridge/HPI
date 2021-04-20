from more_itertools import ilen

from my.discord import messages, activity, Activity
from my.discord import test_remove_link_suppression  # bring test into scope


def test_discord() -> None:
    assert ilen(messages()) > 100

    # get at least 100 activity events
    i: int = 0
    for event in activity():
        assert isinstance(event, Activity)
        i += 1
        if i > 100:
            break
    else:
        assert False
    assert True
