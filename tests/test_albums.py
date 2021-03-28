from more_itertools import ilen

from my.albums import albums


def test_trakt() -> None:
    assert ilen(albums()) > 1
