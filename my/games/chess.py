"""
Parses chess games from chess.com using
https://github.com/seanbreckenridge/chessdotcom_export
"""

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import chess as user_config  # type: ignore[attr-defined]
from my.core import Paths, dataclass


@dataclass
class config(user_config):
    # path[s]/glob to the exported data. These are the resulting json file from 'chessdotcom_export export'
    export_path: Paths


from pathlib import Path
from datetime import datetime
from typing import Iterator, Sequence, Set
from itertools import chain

from my.core import get_files, Stats, LazyLogger, warn_if_empty
from my.core.common import mcachew
from ..utils.common import InputSource

from chessdotcom_export import from_export, Game

logger = LazyLogger(__name__, level="warning")


def inputs() -> Sequence[Path]:
    return get_files(config.export_path)


Results = Iterator[Game]


@mcachew(depends_on=lambda: list(sorted(inputs())), logger=logger)
def history(from_paths: InputSource = inputs) -> Results:
    yield from _merge_histories(*[from_export(str(p)) for p in from_paths()])


@warn_if_empty
def _merge_histories(*sources: Results) -> Results:
    emitted: Set[datetime] = set()
    for g in chain(*sources):
        if g.end_time in emitted:
            continue
        yield g
        emitted.add(g.end_time)


def stats() -> Stats:
    from my.core import stat

    return {**stat(history)}
