"""
Parses the data directory for my MAL export
Uses https://github.com/seanbreckenridge/malexport/
"""

REQUIRES = ["git+https://github.com/seanbreckenridge/malexport"]

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import mal as user_config  # type: ignore[attr-defined]

from pathlib import Path
from datetime import datetime
from typing import Iterator, List, Tuple, NamedTuple, Optional
from functools import lru_cache

from my.core import Stats, LazyLogger, PathIsh, dataclass, make_config, get_files
from my.core.structure import match_structure

from malexport.paths import LocalDir
from malexport.parse.combine import combine, AnimeData, MangaData
from malexport.parse.forum import Post, iter_forum_posts
from malexport.parse.friends import Friend, iter_friends
from malexport.parse.messages import Thread, Message, iter_user_threads
from malexport.parse.recover_deleted_entries import recover_deleted as rec_del, Approved


@dataclass
class mal_config(user_config.export):
    # path[s]/glob to the exported data
    export_path: PathIsh

    # this should be the top level directory, not the zip files or username directories
    # see https://github.com/seanbreckenridge/malexport/#recover_deleted
    zip_backup_path: Optional[PathIsh] = None


config = make_config(mal_config)


logger = LazyLogger(__name__)


# malexport supports multiple accounts
# in its data directory structure
@lru_cache(maxsize=1)
def export_dirs() -> List[Path]:
    base: Path = Path(config.export_path).expanduser().absolute()
    with match_structure(base, expected="animelist.xml") as matches:
        return list(matches)


Export = Tuple[List[AnimeData], List[MangaData]]


@lru_cache(maxsize=2)
def _read_malexport_aux(username: str, *, mtimes: Tuple[float, ...]) -> Export:
    logger.debug(f"reading {username}; cache miss: {mtimes}")
    return combine(username)


def _read_malexport(username: str) -> Export:
    paths = LocalDir.from_username(username).data_dir.rglob("*")
    return _read_malexport_aux(
        username, mtimes=tuple(sorted(map(lambda f: f.stat().st_mtime, paths)))
    )


@lru_cache(maxsize=None)
def _find_deleted_aux(username: str, zips: Tuple[Path, ...]) -> Export:
    return rec_del(
        approved=Approved.parse_from_git_dir(),
        username=username,
        backups=list(zips),
        filter_with_activity=False,
        logger=logger,
    )


def _find_deleted_inputs(username: str) -> Tuple[Path, ...]:
    if config.zip_backup_path is None:
        return tuple()
    directory_for_user: Path = Path(config.zip_backup_path) / username
    return get_files(directory_for_user, sort=True, glob="*.zip")


def _find_deleted(username: str) -> Optional[Export]:
    return _find_deleted_aux(username, _find_deleted_inputs(username))


### Expose all the parsed information from malexport


def anime() -> Iterator[AnimeData]:
    for path in export_dirs():
        anime, _ = _read_malexport(path.stem)
        yield from anime


def manga() -> Iterator[MangaData]:
    for path in export_dirs():
        _, manga = _read_malexport(path.stem)
        yield from manga


def deleted_anime() -> Iterator[AnimeData]:
    for path in export_dirs():
        if export := _find_deleted(path.stem):
            anime, _ = export
            yield from anime


def deleted_manga() -> Iterator[MangaData]:
    for path in export_dirs():
        if export := _find_deleted(path.stem):
            _, manga = export
            yield from manga


class Episode(NamedTuple):
    mal_id: int
    title: str
    episode: int
    at: datetime


# use the combined data when reading history
# since it removes entries you may have deleted
# which still have local history files left over
def episodes() -> Iterator[Episode]:
    for path in export_dirs():
        anime, _ = _read_malexport(path.stem)
        for a in anime:
            for h in a.history:
                yield Episode(
                    mal_id=a.id,
                    title=a.XMLData.title,
                    episode=h.number,
                    at=h.at,
                )


class Chapter(NamedTuple):
    mal_id: int
    title: str
    chapter: int
    at: datetime


def chapters() -> Iterator[Chapter]:
    for path in export_dirs():
        _, manga = _read_malexport(path.stem)
        for m in manga:
            for h in m.history:
                yield Chapter(
                    mal_id=m.id,
                    title=m.XMLData.title,
                    chapter=h.number,
                    at=h.at,
                )


def posts() -> Iterator[Post]:
    for path in export_dirs():
        yield from iter_forum_posts(path.stem)


def threads() -> Iterator[Thread]:
    for path in export_dirs():
        yield from iter_user_threads(path.stem)


def messages() -> Iterator[Message]:
    for t in threads():
        yield from t.messages


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
