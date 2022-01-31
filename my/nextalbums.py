"""
Parses albums from my google sheet
https://github.com/seanbreckenridge/albums
https://sean.fish/s/albums
"""

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import nextalbums as user_config  # type: ignore[attr-defined]
from my.core import Paths, dataclass


@dataclass
class config(user_config):
    # path[s]/glob to the exported data. Resulting file from 'nextalbums export'
    export_path: Paths


from pathlib import Path

from typing import Iterator

from my.core import get_files, Stats, LazyLogger

from nextalbums.export import Album, read_dump


logger = LazyLogger(__name__, level="warning")


# should only ever be one dump, the .job overwrites the file
def _current_albums_export_path() -> Path:
    dump = list(get_files(config.export_path))
    assert len(dump) == 1, "Expected one JSON file as input"
    return dump[0]


def _albums_cached() -> Iterator[Album]:
    return read_dump(_current_albums_export_path())


def history() -> Iterator[Album]:
    """Only return items I've listened to, where the score is not null"""
    yield from filter(lambda a: a.listened, _albums_cached())


def to_listen() -> Iterator[Album]:
    """Albums I have yet to listen to"""
    yield from filter(lambda a: not a.listened and not a.dropped, _albums_cached())


def stats() -> Stats:
    from my.core import stat

    return {
        **stat(history),
        **stat(to_listen),
    }
