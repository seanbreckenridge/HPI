from more_itertools import ilen
from my.smscalls import calls, messages


def test_calls_messags():
    assert ilen(calls()) > 10
    msgs = list(messages())
    assert len(msgs) > 50
    from_me = list(filter(lambda x: x.from_me, msgs))
    assert len(from_me) < len(msgs)
    assert len(from_me) > 10
