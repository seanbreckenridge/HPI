from collections import Counter
from my.old_forums import history


def test_has_old_forums():
    hist = list(history())
    assert len(hist) > 1
    # has more than one forum
    assert len(list(Counter([e.forum_name for e in hist]))) > 1
