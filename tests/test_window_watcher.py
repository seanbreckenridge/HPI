from my.window_watcher import history, Entry


def test_window_watcher():
    items = list(history())
    assert len(items) > 5
    assert isinstance(items[0], Entry)
