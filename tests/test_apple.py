from more_itertools import ilen


from .common import skip_if_not_seanb


@skip_if_not_seanb
def test_apple_types() -> None:
    from my.apple.privacy_export import (
        events,
        Game,
        GameAchievement,
        GameLeaderboardData,
        Location,
    )

    all_ev = list(events())
    assert len(all_ev) > 10
    all_types = set([Game, GameAchievement, GameLeaderboardData, Location])
    assert all_types == set(map(type, all_ev))
    # make sure we parsed everything without errors
    assert ilen(filter(lambda e: isinstance(e, Exception), all_ev)) == 0
