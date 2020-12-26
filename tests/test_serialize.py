import pytest
import json
from datetime import datetime

from my.zsh import history, Entry
from my.core.serialize import dumps

from more_itertools import take


def test_serialize_succeeds():
    # single item
    dt = datetime.now()
    item = Entry(dt=dt, command="something", duration=2)
    sitem = dumps(item)  # encode
    decoded = json.loads(sitem)  # then decode back
    assert decoded["dt"] == int(dt.timestamp())
    assert decoded["command"] == "something"
    assert decoded["duration"] == 2

    # list, make sure number of items matches
    items = take(100, history())
    assert len(items) == 100
    assert len(json.loads(dumps(items))) == 100


def test_serialize_fails():
    class Something:
        pass

    with pytest.raises(TypeError):
        dumps([Something()])
