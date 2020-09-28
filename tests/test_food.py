from more_itertools import ilen

from my.food import water, food


def test_water() -> None:
    assert ilen(water()) >= 1


def test_food() -> None:
    assert ilen(food()) >= 1
