from more_itertools import ilen

from my.body import weight, shower, food, water


def test_body() -> None:

    for func in (weight, shower, food, water):
        assert ilen(func()) >= 1
