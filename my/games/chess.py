"""
Parses chess games from chess.com using
https://github.com/seanbreckenridge/chessdotcom_export
"""

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import chess as user_config

from dataclasses import dataclass

from ..core import Paths


@dataclass
class chess(user_config):
    # path[s]/glob to the exported data. These are the resulting json file from 'chessdotcom_export export'
    export_path: Paths


from ..core.cfg import make_config

config = make_config(chess)

#######

from pathlib import Path
from datetime import datetime
from typing import Iterator, Sequence, Dict, Any, Set
from itertools import chain

from ..core import get_files, Stats

from chessdotcom_export import from_export
from chessdotcom_export.model import Game


def inputs() -> Sequence[Path]:
    """
    Get the exported chess.com dumps
    """
    return get_files(config.export_path)


Json = Dict[str, Any]
Results = Iterator[Game]


def history(from_paths=inputs) -> Results:
    yield from _merge_histories(*map(from_export, from_paths()))


def _merge_histories(*sources: Results) -> Results:
    emitted: Set[datetime] = set()
    for g in chain(*sources):
        if g.end_time in emitted:
            continue
        yield g
        emitted.add(g.end_time)


def stats() -> Stats:
    from ..core import stat

    return {**stat(history)}
