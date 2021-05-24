from more_itertools import ilen

from my.grouvee import played


def test_grouvee() -> None:
    assert ilen(played()) > 1
