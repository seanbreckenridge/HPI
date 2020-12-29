"""
Parses a basic logfile of my laptop battery
This logs once per minute, and is part of my menu bar script
https://sean.fish/d/.config/i3blocks/blocks/battery
"""

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import battery as user_config

from dataclasses import dataclass

from .core import Paths


@dataclass
class battery(user_config):
    # path/glob to the battery logfile
    export_path: Paths


from .core.cfg import make_config

config = make_config(battery)

#######

import csv
from typing import Sequence
from pathlib import Path

from .core import get_files, warn_if_empty, Stats
from .core.common import listify
from .core.time import parse_datetime_sec
from .core.file import filter_subfile_matches


@listify
def inputs() -> Sequence[Path]:  # type: ignore[misc]
    """Returns all battery log/datafiles"""
    yield from get_files(config.export_path)


from datetime import datetime
from typing import NamedTuple, Iterator, Set, Tuple
from itertools import chain


# represents one battery entry, the status at some point
class Entry(NamedTuple):
    dt: datetime
    percentage: int
    status: str


Results = Iterator[Entry]


def history(from_paths=inputs) -> Results:
    yield from _merge_histories(*map(_parse_file, filter_subfile_matches(from_paths())))


@warn_if_empty
def _merge_histories(*sources: Results) -> Results:
    emitted: Set[Tuple[datetime, int]] = set()
    for e in chain(*sources):
        key = (e.dt, e.percentage)
        if key in emitted:
            continue
        yield e
        emitted.add(key)


def _parse_file(histfile: Path) -> Results:
    with histfile.open("r", encoding="utf-8", newline="") as f:
        csv_reader = csv.reader(
            f, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )
        for row in csv_reader:
            yield Entry(
                dt=parse_datetime_sec(row[0]), percentage=int(row[1]), status=row[2]
            )


def stats() -> Stats:
    from .core import stat

    return {**stat(history)}
