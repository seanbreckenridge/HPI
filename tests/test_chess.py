from more_itertools import ilen

from my.games.chess import history


def test_chess():
    assert ilen(history()) >= 1
