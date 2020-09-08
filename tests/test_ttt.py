from my.ttt import history, Entry


def test_ttt():
    items = list(history())
    assert len(items) > 5
    assert isinstance(items[0], Entry)
