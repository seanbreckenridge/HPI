from more_itertools import ilen

from my.body import weight, teeth, shower


def test_body() -> None:

    for func in (weight, teeth, shower):
        assert ilen(func()) >= 1
