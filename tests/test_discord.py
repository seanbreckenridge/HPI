from more_itertools import ilen

from my.discord import messages, activity


def test_discord() -> None:
    assert ilen(messages()) > 100

    # get at least 100 activity events
    i: int = 0
    for event in activity():
        assert isinstance(event, dict)
        i += 1
        if i > 100:
            break
    else:
        assert False
    assert True
