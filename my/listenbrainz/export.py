"""
Parses scrobbles from https://listenbrainz.org/ using
https://github.com/seanbreckenridge/listenbrainz_export
"""

REQUIRES = ["git+https://github.com/seanbreckenridge/listenbrainz_export"]

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import listenbrainz as user_config  # type: ignore[attr-defined]


from pathlib import Path
from typing import Iterator, Sequence
from itertools import chain

from listenbrainz_export.parse import Listen, iter_listens
from more_itertools import unique_everseen

from my.core import get_files, Stats, LazyLogger, Paths, dataclass
from my.utils.common import InputSource


@dataclass
class config(user_config):
    # path[s]/glob to the exported data
    export_path: Paths


logger = LazyLogger(__name__, level="warning")


def inputs() -> Sequence[Path]:
    return get_files(config.export_path)


Results = Iterator[Listen]


def _parse_export_file(p: Path) -> Results:
    # remove any items which have null as listen date
    # (may have been listening to something when export happened)
    yield from filter(lambda l: l.listened_at is not None, iter_listens(str(p)))


def history(from_paths: InputSource = inputs) -> Results:
    yield from unique_everseen(
        chain(*(_parse_export_file(p) for p in from_paths())),
        key=lambda l: l.listened_at,
    )


def stats() -> Stats:
    from my.core import stat

    return {**stat(history)}
