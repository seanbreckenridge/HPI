from more_itertools import ilen

from my.browsing import history


def test_browsing_contents():
    assert ilen(history()) > 100
