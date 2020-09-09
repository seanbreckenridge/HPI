"""
Parses the spotify GPDR Export
"""

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import spotify as user_config

from dataclasses import dataclass
from .core import PathIsh


@dataclass
class spotify(user_config):
    gdpr_dir: PathIsh  # path to unpacked GDPR archive


from .core.cfg import make_config

config = make_config(spotify)

import os
import json
from datetime import date
from pathlib import Path
from itertools import chain
from typing import Iterator, Dict, Any, NamedTuple, List, Set, Tuple

from .core.error import Res
from .core import get_files

from .core.common import LazyLogger

logger = LazyLogger(__name__)


class Song(NamedTuple):
    name: str
    artist: str
    album: str


class Playlist(NamedTuple):
    name: str
    last_modified: date
    songs: List[Song]


Playlists = Iterator[Res[Playlist]]
Songs = Iterator[Res[Song]]


def playlists() -> Playlists:
    # get files 2 levels deep into the export
    gdpr_dir = str(Path(config.gdpr_dir).expanduser().absolute())  # expand path
    files = get_files(config.gdpr_dir, glob="*.json")
    handler_map = {
        "Follow": None,
        "Inferences": None,
        "Payments": None,
        "Playlist": _parse_playlists,
        "StreamingHistory": None,  # doesnt save any of the old play history, not worth parsing
        "Userdata": None,
        "YourLibrary": None,
    }
    for f in files:
        handler: Any
        for prefix, h in handler_map.items():
            if not str(f).startswith(os.path.join(gdpr_dir, prefix)):
                continue
            handler = h
            break
        else:
            e = RuntimeError(f"Unhandled file: {f}")
            logger.debug(str(e))
            yield e
            continue

        if handler is None:
            # explicitly ignored
            continue

        if f.is_dir():
            # rglob("*") matches directories, as well as any subredirectories/json files in those
            # this is here exclusively for the messages dir, which has a larger structure
            # json files from inside the dirs are still picked up by rglob
            continue

        if f.suffix != ".json":
            continue

        j = json.loads(f.read_text())
        yield from handler(j)


def songs() -> Songs:
    emitted: Set[Tuple[str, str, str]] = set()
    for e in chain(*map(lambda p: p.songs, playlists())):
        if isinstance(e, Exception):
            yield e
            continue
        key = (e.name, e.artist, e.album)
        if key in emitted:
            # logger.debug('ignoring %s: %s', key, e)
            continue
        yield e
        emitted.add(key)


def stats():
    from .core import stat

    return {
        **stat(playlists),
        **stat(songs),
    }


def _parse_playlists(d: Dict) -> Iterator[Playlist]:
    # parse, then filter
    # make sure this playlist has more than one artist
    # if its just one artist, its probably just an album
    yield from filter(
        lambda p: len(set([s.artist for s in p.songs])) > 1, _parse_all_playlists(d)
    )


def _parse_all_playlists(d: Dict) -> Iterator[Playlist]:
    for plist in d["playlists"]:
        if plist["numberOfFollowers"] > 50:
            logger.debug(
                f"Ignoring playlist: {plist['name']}, too many followers to be one of my playlists"
            )
            continue
        yield Playlist(
            name=plist["name"],
            last_modified=_parse_date(plist["lastModifiedDate"]),
            songs=list(map(_parse_song, plist["items"])),
        )


def _parse_song(song_info: Dict) -> Song:
    tr: Dict = song_info["track"]
    return Song(
        name=tr["trackName"],
        artist=tr["artistName"],
        album=tr["albumName"],
    )


def _parse_date(date_str: str) -> date:
    date_info: List[int] = list(map(int, date_str.split("-")))
    return date(year=date_info[0], month=date_info[1], day=date_info[2])
