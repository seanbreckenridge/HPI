from my.battery import history, Entry


def test_battery():
    items = list(history())
    assert len(items) > 5
    assert isinstance(items[0], Entry)
