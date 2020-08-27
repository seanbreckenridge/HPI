import os

from my.todotxt import Todo, history

def test_todotxt():
    t = list(history())
    assert isinstance(t[0], Todo)
    assert len(t) > 10
