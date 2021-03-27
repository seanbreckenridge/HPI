from more_itertools import ilen

from my.trakt import history, ratings


def test_trakt() -> None:
    assert ilen(history()) > 1
    assert ilen(ratings()) > 1
