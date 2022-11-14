"""
Timed Rubiks Cube Solve History from multiple sources using
https://github.com/seanbreckenridge/scramble-history
"""

from pathlib import Path
from my.core import dataclass, PathIsh, make_config

from my.config import scramble as user_config  # type: ignore[attr-defined]


@dataclass
class mpv_config(user_config.history):
    sourcemap: PathIsh
    config: PathIsh


config = make_config(mpv_config)

from typing import Iterator
from functools import lru_cache

from scramble_history.config import parse_config_file, ConfigPaths
from scramble_history.models import Solve
from scramble_history.source_merger import merge as merge_solves


@lru_cache(maxsize=None)
def scramble_conf() -> ConfigPaths:
    return parse_config_file(Path(config.config).expanduser())


def solves() -> Iterator[Solve]:
    yield from merge_solves(
        sourcemap_file=Path(config.sourcemap).expanduser(), conf=scramble_conf()
    )
