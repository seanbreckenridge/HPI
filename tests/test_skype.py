from datetime import datetime


def test_skype() -> None:
    import my.skype

    ts = list(my.skype.timestamps())
    assert len(ts) > 1
    timestamp = ts[0]
    assert isinstance(timestamp, datetime)
