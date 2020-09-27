from more_itertools import ilen


def test_body() -> None:
    from my.body import weight, teeth, shower

    for func in (weight, teeth, shower):
        assert ilen(func()) >= 1
