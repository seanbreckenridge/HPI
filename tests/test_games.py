from more_itertools import ilen

from my.league.export import history
from my.steam.scraper import games, achievements


def test_league() -> None:
    gs = list(history())
    assert len(gs) > 50
    assert len(gs[0].players) == 10


def test_steam() -> None:
    assert ilen(games()) > 10
    ach = list(achievements())
    assert any([a.game_name == "Counter-Strike: Global Offensive" for a in ach])
