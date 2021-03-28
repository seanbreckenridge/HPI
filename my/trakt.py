"""
Parses the dump of my movies/tv shows history and watchlist from https://trakt.tv/
Uses https://github.com/seanbreckenridge/traktexport
"""

REQUIRES = ["traktexport"]

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import trakt as user_config  # type: ignore[attr-defined]
from my.core import Paths, dataclass


@dataclass
class config(user_config):
    # path[s]/glob to the exported data. These are the resulting json file from 'traktexport export'
    export_path: Paths


from pathlib import Path
from typing import Iterator, Dict, Any
from functools import lru_cache

from more_itertools import last

from my.core import get_files, Stats, LazyLogger
from my.core.common import mcachew

import traktexport.dal as D

logger = LazyLogger(__name__, level="warning")


def _latest_input() -> Path:
    """Since the exports are complete exports, can just use the most recent export"""
    return last(sorted(get_files(config.export_path)))


# should typically only parse the latest dump when the info
# isn't cached in the cachew dbs
@lru_cache(maxsize=None)
def _read_trakt_export(p: Path) -> D.TraktExport:
    return D.parse_export(p)


### Expose all the parsed information from traktexport.dal


def profile_stats() -> Dict[str, Any]:
    # read the 'stats' key directly from the JSON file
    return D._read_unparsed(_latest_input())["stats"]


@mcachew(depends_on=_latest_input, logger=logger)
def followers() -> Iterator[D.Follow]:
    yield from _read_trakt_export(_latest_input()).followers


@mcachew(depends_on=_latest_input, logger=logger)
def likes() -> Iterator[D.Like]:
    yield from _read_trakt_export(_latest_input()).likes


@mcachew(depends_on=_latest_input, logger=logger)
def watchlist() -> Iterator[D.WatchListEntry]:
    yield from _read_trakt_export(_latest_input()).watchlist


@mcachew(depends_on=_latest_input, logger=logger)
def ratings() -> Iterator[D.Rating]:
    yield from _read_trakt_export(_latest_input()).ratings


@mcachew(depends_on=_latest_input, logger=logger)
def history() -> Iterator[D.HistoryEntry]:
    yield from _read_trakt_export(_latest_input()).history


def stats() -> Stats:
    from my.core import stat

    return {
        **stat(followers),
        **stat(likes),
        **stat(watchlist),
        **stat(ratings),
        **stat(history),
    }
