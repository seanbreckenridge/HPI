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

from my.core import Stats, LazyLogger, PathIsh, dataclass
from my.core.common import mcachew
from my.core.structure import match_structure

from malexport.parse.combine import combine, AnimeData, MangaData
from malexport.parse.forum import Post, iter_forum_posts
from malexport.parse.friends import Friend, iter_friends


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


# use the combined data when reading history
# since it removes entries you may have deleted
# which still have local history files left over
@mcachew(depends_on=_history_depends_on, logger=logger)
def episodes() -> Iterator[Episode]:
    for path in export_dirs():
        anime, _ = _read_malexport(path.stem)
        for a in anime:
            for h in a.history:
                yield Episode(
                    mal_id=a.id,
                    title=a.title,
                    episode=h.number,
                    at=h.at,
                )


class Chapter(NamedTuple):
    mal_id: int
    title: str
    chapter: int
    at: datetime


@mcachew(depends_on=_history_depends_on, logger=logger)
def chapters() -> Iterator[Chapter]:
    for path in export_dirs():
        _, manga = _read_malexport(path.stem)
        for m in manga:
            for h in m.history:
                yield Chapter(
                    mal_id=m.id,
                    title=m.title,
                    chapter=h.number,
                    at=h.at,
                )


def posts() -> Iterator[Post]:
    for path in export_dirs():
        yield from iter_forum_posts(path.stem)


def friends() -> Iterator[Friend]:
    for path in export_dirs():
        yield from iter_friends(path.stem)


def stats() -> Stats:
    from my.core import stat

    return {
        **stat(anime),
        **stat(manga),
        **stat(chapters),
        **stat(episodes),
        **stat(posts),
        **stat(friends),
    }
