from more_itertools import ilen

from my.firefox import history


def test_browsing_contents():
    assert ilen(history()) > 5
