from more_itertools import ilen

from my.location.all import locations


def test_locations() -> None:
    assert ilen(locations()) > 100
