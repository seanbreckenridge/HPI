from more_itertools import ilen, last

from my.browsing import history


def test_browsing_contents():
    assert ilen(history()) > 100
