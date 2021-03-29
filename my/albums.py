"""
Parses albums from my google sheet
https://github.com/seanbreckenridge/albums
https://sean.fish/s/albums
"""

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import albums as user_config  # type: ignore[attr-defined]
from my.core import Paths, dataclass


@dataclass
class config(user_config):
    # path[s]/glob to the exported data. Resulting file from 'nextalbums export'
    export_path: Paths


from pathlib import Path

from typing import Iterator

from my.core import get_files, Stats, LazyLogger
from my.core.common import mcachew

from nextalbums.export import Album, read_dump


logger = LazyLogger(__name__, level="warning")


# should only ever be one dump, the .job overwrites the file
def _current_albums_export_path() -> Path:
    return get_files(config.export_path)[0]


def _cachew_depends_on() -> float:
    return _current_albums_export_path().stat().st_mtime


@mcachew(depends_on=_cachew_depends_on, logger=logger)
def _albums_cached() -> Iterator[Album]:
    # read the 'stats' key directly from the JSON file
    return read_dump(_current_albums_export_path())


@mcachew(depends_on=_cachew_depends_on, logger=logger)
def history() -> Iterator[Album]:
    """Only return items I've listened to, where the score is not null"""
    yield from filter(lambda a: a.score is not None, _albums_cached())


@mcachew(depends_on=_cachew_depends_on, logger=logger)
def to_listen() -> Iterator[Album]:
    """Items I have yet to listen to"""
    yield from filter(lambda a: a.score is None, _albums_cached())


def stats() -> Stats:
    from my.core import stat

    return {
        **stat(history),
        **stat(to_listen),
    }
