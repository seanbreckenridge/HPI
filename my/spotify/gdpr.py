"""
Parses the spotify GPDR Export
"""

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import spotify as user_config  # type: ignore[attr-defined]

from my.core import PathIsh, Stats, dataclass


@dataclass
class config(user_config.gdpr):
    gdpr_dir: PathIsh  # path to unpacked GDPR archive


import os
import json
from datetime import date
from pathlib import Path
from typing import Iterator, Any, NamedTuple, List, Set, Tuple, Sequence, Optional

from my.core import Res, get_files, LazyLogger, Json

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


def inputs(gdpr_dir: Optional[PathIsh] = None) -> Sequence[Path]:
    chosen: PathIsh = gdpr_dir if gdpr_dir is not None else config.gdpr_dir
    echosen = Path(chosen).expanduser().absolute()
    return get_files(echosen, glob="*.json")


def playlists() -> Playlists:
    gdpr_dir = str(Path(config.gdpr_dir).expanduser().absolute())  # expand path
    files = inputs(gdpr_dir)
    handler_map = {
        "Follow": None,
        "Inferences": None,
        "Payments": None,
        "Playlist": _filter_playlists,
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
            if f.is_dir():
                continue
            else:
                e = RuntimeError(f"Unhandled file: {f}")
                logger.debug(str(e))
                yield e
                continue

        if handler is None:
            # explicitly ignored
            continue

        if f.suffix != ".json":
            continue

        j = json.loads(f.read_text())
        yield from handler(j)


def songs() -> Songs:
    emitted: Set[Tuple[str, str, str]] = set()
    for p in playlists():
        if isinstance(p, Exception):
            yield p
            continue
        for song in p.songs:
            key = (song.name, song.artist, song.album)
            if key in emitted:
                continue
            yield song
            emitted.add(key)


def stats() -> Stats:
    from my.core import stat

    return {
        **stat(playlists),
        **stat(songs),
    }


def _filter_playlists(d: Json) -> Iterator[Playlist]:
    # parse, then filter
    # make sure this playlist has more than one artist
    # if its just one artist, its probably just an album
    # that's been classified as a playlist
    for p in _parse_all_playlists(d):
        if len(set([s.artist for s in p.songs])) > 1:
            yield p


def _parse_all_playlists(d: Json) -> Iterator[Playlist]:
    for plist in d["playlists"]:
        if plist["numberOfFollowers"] > 50:
            logger.debug(
                f"Ignoring playlist: {plist['name']}, too many followers to be one of my playlists"
            )
            continue
        songs: List[Song] = [_parse_song(b) for b in plist["items"]]
        yield Playlist(
            name=plist["name"],
            last_modified=_parse_date(plist["lastModifiedDate"]),
            songs=songs,
        )


def _parse_song(song_info: Json) -> Song:
    tr: Json = song_info["track"]
    return Song(
        name=tr["trackName"],
        artist=tr["artistName"],
        album=tr["albumName"],
    )


def _parse_date(date_str: str) -> date:
    date_info: List[int] = list(map(int, date_str.split("-")))
    return date(year=date_info[0], month=date_info[1], day=date_info[2])
