from more_itertools import ilen

from my.body_log import weight, shower


def test_body() -> None:

    for func in (weight, shower):
        assert ilen(func()) >= 1
