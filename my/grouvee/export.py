"""
Parses the CSV export from https://www.grouvee.com/
"""

REQUIRES = ["git+https://github.com/seanbreckenridge/grouvee_export"]

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import grouvee as user_config  # type: ignore[attr-defined]

from pathlib import Path
from typing import Iterator, List
from functools import lru_cache

from more_itertools import last
import grouvee_export.dal as G

from my.core import get_files, Stats, Paths, dataclass


@dataclass
class config(user_config.export):
    # path[s]/glob to the exported CSV files
    export_path: Paths


def _latest_input() -> Path:
    """Since the exports are complete exports, can just use the most recent export"""
    return last(sorted(get_files(config.export_path), key=lambda p: p.stat().st_mtime))


# should typically only parse the latest dump
@lru_cache(maxsize=None)
def _read_grouvee_export(p: Path) -> List[G.Game]:
    return list(G.parse_export(p))


def games() -> Iterator[G.Game]:
    yield from _read_grouvee_export(_latest_input())


def _filter_games_for_shelf(name: str) -> Iterator[G.Game]:
    for game in games():
        if name in [s.name for s in game.shelves]:
            yield game


def played() -> Iterator[G.Game]:
    """Games I've Played"""
    yield from _filter_games_for_shelf("Played")


def watched() -> Iterator[G.Game]:
    """Games I've watched, not played"""
    yield from _filter_games_for_shelf("Watched")


def backlog() -> Iterator[G.Game]:
    """Games on my backlog"""
    yield from _filter_games_for_shelf("Backlog")


def wish_list() -> Iterator[G.Game]:
    """Games on my wish list"""
    yield from _filter_games_for_shelf("Wish List")


def stats() -> Stats:
    from my.core import stat

    return {
        **stat(played),
        **stat(watched),
        **stat(backlog),
        **stat(wish_list),
    }
