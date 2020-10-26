from more_itertools import ilen

from my.apple import events, Game, GameAchievement, GameLeaderboardData, Location


def test_apple_types():
    all_ev = list(events())
    assert len(all_ev) > 10
    all_types = set([Game, GameAchievement, GameLeaderboardData, Location])
    assert all_types == set(map(type, all_ev))
    # make sure we parsed everything without errors
    assert ilen(filter(lambda e: isinstance(e, Exception), all_ev)) == 0
