"""
Parses chess games from chess.com/lichess.org using
https://github.com/seanbreckenridge/chess_export
"""

REQUIRES = ["git+https://github.com/seanbreckenridge/chess_export"]

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import chess as user_config  # type: ignore[attr-defined]
from my.core import Paths, dataclass


@dataclass
class config(user_config):
    # path[s]/glob to the exported data. These are the resulting JSON files from 'chess_export ... export'
    export_path: Paths


from pathlib import Path
from datetime import datetime
from typing import Iterator, Sequence, Set, List, Union
from itertools import chain

from my.core import get_files, Stats, LazyLogger, warn_if_empty
from my.core.common import mcachew
from .utils.common import InputSource

import chess_export.chessdotcom.model as cmodel
import chess_export.lichess.model as lmodel

logger = LazyLogger(__name__, level="warning")


def inputs() -> Sequence[Path]:
    return get_files(config.export_path)


# TODO: make extendible? Not sure if anyone has any other things they need to include here though...
Results = Iterator[Union[cmodel.ChessDotComGame, lmodel.LichessGame]]


def _cachew_depends_on(for_paths: InputSource = inputs) -> List[float]:
    return [p.stat().st_mtime for p in for_paths()]


def _parse_export_file(p: Path) -> Results:
    # try one, else the other
    # typically this raises a KeyError since the JSON didn't match
    # what the NamedTuple expects
    try:
        yield from lmodel.from_export(str(p))
    except Exception:
        yield from cmodel.from_export(str(p))


@mcachew(depends_on=_cachew_depends_on, logger=logger)
def history(from_paths: InputSource = inputs) -> Results:
    yield from _merge_histories(*(_parse_export_file(p) for p in from_paths()))


@warn_if_empty
def _merge_histories(*sources: Results) -> Results:
    emitted: Set[datetime] = set()
    for g in chain(*sources):
        if g.end_time in emitted:  # exists on both lichess and chess.com model
            continue
        yield g
        emitted.add(g.end_time)


def stats() -> Stats:
    from my.core import stat

    return {**stat(history)}
