from my.core.common import make_dict

from more_itertools import ilen

from my.reddit import events, inputs, saved, _dal, pushshift_comments


def test_reddit_has_data() -> None:

    assert ilen(events()) > 10
    assert ilen(saved()) > 10
    assert ilen(inputs()) >= 1
    assert ilen(pushshift_comments()) > ilen(_dal().comments())


def test_saves() -> None:
    # TODO not sure if this is necesasry anymore?
    saves = list(saved())
    # just check that they are unique..
    assert len(make_dict(saves, key=lambda s: s.sid)) > 10
