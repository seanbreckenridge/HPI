"""
Timed Rubiks Cube Solve History from multiple sources using
https://github.com/seanbreckenridge/scramble-history
"""

REQUIRES = ["git+https://github.com/seanbreckenridge/scramble-history"]

from pathlib import Path
from typing import Optional
from my.core import dataclass, PathIsh, make_config

from my.config import scramble as user_config  # type: ignore[attr-defined]


@dataclass
class scramble_config(user_config.history):
    config_dir: Optional[PathIsh] = None


config = make_config(scramble_config)

from typing import Iterator

from scramble_history.__main__ import (
    scramble_history_config_dir,
    conf_name,
    sourcemap_name,
)
from scramble_history.config import parse_config_file
from scramble_history.models import Solve
from scramble_history.source_merger import merge as merge_solves

config_dir = Path(config.config_dir or scramble_history_config_dir).expanduser()


parsed_conf = parse_config_file(config_dir / conf_name)


def solves() -> Iterator[Solve]:
    yield from merge_solves(sourcemap_file=config_dir / sourcemap_name, conf=parsed_conf)
