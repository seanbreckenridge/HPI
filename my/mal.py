"""
Parses the data directory for my MAL export
Uses https://github.com/seanbreckenridge/malexport/
"""

REQUIRES = ["git+https://github.com/seanbreckenridge/malexport"]

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import mal as user_config  # type: ignore[attr-defined]

from pathlib import Path
from datetime import datetime
from typing import Iterator, List, Tuple, NamedTuple
from functools import lru_cache

from my.core import get_files, Stats, LazyLogger, PathIsh, dataclass
from my.core.common import mcachew
from my.core.structure import match_structure

from malexport.parse.combine import combine, AnimeData, MangaData, ListType
from malexport.parse.forum import Post, iter_forum_posts
from malexport.parse.history import parse_history_dir


@dataclass
class config(user_config):
    # path[s]/glob to the exported data
    export_path: PathIsh


logger = LazyLogger(__name__, level="warning")


# malexport supports multiple accounts
# in its data directory structure
@lru_cache(maxsize=1)
def export_dirs() -> List[Path]:
    base: Path = Path(config.export_path).expanduser().absolute()
    with match_structure(base, expected="animelist.xml") as matches:
        return list(matches)


def _history_depends_on() -> List[float]:
    json_history_files: List[Path] = []
    for p in export_dirs():
        json_history_files.extend(list((p / "history").rglob("*.json")))
    json_history_files.sort()
    return [p.lstat().st_mtime for p in json_history_files]


def _forum_depends_on() -> List[float]:
    indexes = []
    for p in export_dirs():
        indexes.append(p / "forum" / "index.json")
    return [p.lstat().st_mtime for p in indexes]


Export = Tuple[List[AnimeData], List[MangaData]]


@lru_cache(maxsize=None)
def _read_malexport(username: str) -> Export:
    return combine(username)


### Expose all the parsed information from malexport


def anime() -> Iterator[AnimeData]:
    for path in export_dirs():
        anime, _ = _read_malexport(path.stem)
        yield from anime


def manga() -> Iterator[MangaData]:
    for path in export_dirs():
        _, manga = _read_malexport(path.stem)
        yield from manga


class Episode(NamedTuple):
    mal_id: int
    title: str
    episode: int
    at: datetime


# parse the directory directly instead of parsing all data
# and then extracting the history from it
@mcachew(depends_on=_history_depends_on, logger=logger)
def episodes() -> Iterator[Episode]:
    for path in export_dirs():
        for hist in parse_history_dir(path / "history" / "anime", ListType.ANIME):
            for ep in hist.entries:
                yield Episode(
                    mal_id=hist.mal_id, title=hist.title, episode=ep.number, at=ep.at
                )


class Chapter(NamedTuple):
    mal_id: int
    title: str
    chapter: int
    at: datetime


@mcachew(depends_on=_history_depends_on, logger=logger)
def chapters() -> Iterator[Chapter]:
    for path in export_dirs():
        for hist in parse_history_dir(path / "history" / "manga", ListType.MANGA):
            for ch in hist.entries:
                yield Chapter(
                    mal_id=hist.mal_id, title=hist.title, chapter=ch.number, at=ch.at
                )


@mcachew(depends_on=_forum_depends_on, logger=logger)
def posts() -> Iterator[Post]:
    for path in export_dirs():
        yield from iter_forum_posts(path.stem)


def stats() -> Stats:
    from my.core import stat

    return {
        **stat(anime),
        **stat(manga),
        **stat(chapters),
        **stat(episodes),
        **stat(posts),
    }
