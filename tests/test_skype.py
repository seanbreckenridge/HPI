from datetime import datetime

import my.skype


def test_skype() -> None:

    ts = list(my.skype.timestamps())
    assert len(ts) > 1
    timestamp = ts[0]
    assert isinstance(timestamp, datetime)
