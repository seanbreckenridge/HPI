"""
Parses history from https://github.com/seanbreckenridge/ttt
"""

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import ttt as user_config  # type: ignore[attr-defined]

import csv
from pathlib import Path
from datetime import datetime
from typing import NamedTuple, Iterator, Sequence, Optional
from itertools import chain

from more_itertools import unique_everseen

from my.core import get_files, Stats, Paths, dataclass
from my.utils.time import parse_datetime_sec
from my.utils.common import InputSource


@dataclass
class config(user_config):
    # path[s]/glob to the backed up ttt history files
    # (can be a list if you want to provide the live file)
    export_path: Paths


def inputs() -> Sequence[Path]:
    return get_files(config.export_path)


# represents one history entry (command)
class Entry(NamedTuple):
    dt: datetime
    command: str
    directory: Optional[str]


Results = Iterator[Entry]


def history(from_paths: InputSource = inputs) -> Results:
    yield from unique_everseen(
        chain(*map(_parse_file, from_paths())),
        key=lambda e: (
            e.dt,
            e.command,
        ),
    )


def _parse_file(histfile: Path) -> Results:
    # TODO: helper function to read 'regular' QUOTE_MINIMAL csv files
    # without failing due to encoding errors?
    with histfile.open("r", encoding="utf-8", newline="") as f:
        csv_reader = csv.reader(
            f, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )
        for row in csv_reader:
            yield Entry(
                dt=parse_datetime_sec(row[0]),
                command=row[2],
                directory=None if row[1] == "-" else row[1],
            )


def stats() -> Stats:
    from my.core import stat

    return {**stat(history)}
