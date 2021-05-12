import my.twitch.all


def test_twitch() -> None:
    events = list(my.twitch.all.events())
    assert len(events) > 1
