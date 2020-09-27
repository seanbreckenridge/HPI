from more_itertools import ilen

from my.food import water


def test_water() -> None:
    assert ilen(water()) >= 1
