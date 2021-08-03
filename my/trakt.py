"""
Parses the dump of my movies/tv shows history and watchlist from https://trakt.tv/
Uses https://github.com/seanbreckenridge/traktexport
"""

REQUIRES = ["git+https://github.com/seanbreckenridge/traktexport"]

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import trakt as user_config  # type: ignore[attr-defined]

from pathlib import Path
from typing import Iterator, Dict, Any, Sequence
from functools import lru_cache

import traktexport.dal as D
from traktexport.merge import read_and_merge_exports

from my.core import get_files, Stats, LazyLogger, Paths, dataclass
from my.core.common import mcachew


@dataclass
class config(user_config):
    # path[s]/glob to the exported data. These are the resulting json file from 'traktexport export'
    export_path: Paths


logger = LazyLogger(__name__, level="warning")


def inputs() -> Sequence[Path]:
    return get_files(config.export_path)


@lru_cache(maxsize=None)
def _read_trakt_exports() -> D.FullTraktExport:
    return read_and_merge_exports(list(map(str, inputs())))


### Expose all the parsed information from traktexport.dal


def profile_stats() -> Dict[str, Any]:
    # read the 'stats' key directly from the JSON file
    return _read_trakt_exports().stats


@mcachew(depends_on=inputs, logger=logger)
def followers() -> Iterator[D.Follow]:
    yield from _read_trakt_exports().followers


@mcachew(depends_on=inputs, logger=logger)
def likes() -> Iterator[D.Like]:
    yield from _read_trakt_exports().likes


@mcachew(depends_on=inputs, logger=logger)
def watchlist() -> Iterator[D.WatchListEntry]:
    yield from _read_trakt_exports().watchlist


@mcachew(depends_on=inputs, logger=logger)
def ratings() -> Iterator[D.Rating]:
    yield from _read_trakt_exports().ratings


@mcachew(depends_on=inputs, logger=logger)
def history() -> Iterator[D.HistoryEntry]:
    yield from _read_trakt_exports().history


def stats() -> Stats:
    from my.core import stat

    return {
        **stat(followers),
        **stat(likes),
        **stat(watchlist),
        **stat(ratings),
        **stat(history),
    }
