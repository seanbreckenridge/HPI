from more_itertools import ilen

def test() -> None:
    from my.body.weight import history
    assert ilen(history()) >= 1


