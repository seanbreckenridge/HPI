from more_itertools import ilen

from my.listenbrainz import history


def test_listenbrainz() -> None:
    assert ilen(history()) > 1
