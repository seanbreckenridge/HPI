import os
from more_itertools import ilen

from my.todotxt import Todo, completed, events


def test_todotxt():
    t = list(completed())
    assert isinstance(t[0], Todo)
    assert len(t) > 10
    assert ilen(events()) >= 1
