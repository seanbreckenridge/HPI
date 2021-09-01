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

from malexport.parse.combine import combine, AnimeData, MangaData
from malexport.parse.forum import Post, iter_forum_posts


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


# use the XML files from the export
# to determine if cache has expired
def _cachew_depends_on() -> List[float]:
    xml_files = []
    for p in export_dirs():
        xml_files.extend(list(get_files(p / "*.xml")))
    return [p.lstat().st_mtime for p in xml_files]


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


@mcachew(depends_on=_cachew_depends_on, logger=logger)
def episodes() -> Iterator[Episode]:
    for path in export_dirs():
        anime, _ = _read_malexport(path.stem)
        for a in anime:
            for h in a.history:
                yield Episode(mal_id=a.id, title=a.title, episode=h.number, at=h.at)


class Chapter(NamedTuple):
    mal_id: int
    title: str
    chapter: int
    at: datetime


@mcachew(depends_on=_cachew_depends_on, logger=logger)
def chapters() -> Iterator[Chapter]:
    for path in export_dirs():
        _, manga = _read_malexport(path.stem)
        for m in manga:
            for h in m.history:
                yield Chapter(mal_id=m.id, title=m.title, chapter=h.number, at=h.at)


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
