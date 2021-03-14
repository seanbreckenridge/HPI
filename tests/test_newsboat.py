from more_itertools import ilen

import my.newsboat


def test_newsboat() -> None:
    assert ilen(my.newsboat.subscription_history()) >= 1
    computes = list(my.newsboat.events())
    assert {True, False} == set([r.added for r in computes])
