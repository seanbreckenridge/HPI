"""
Parses history from https://github.com/seanbreckenridge/ttt
"""

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import ttt as user_config  # type: ignore[attr-defined]

from typing import Optional

from my.core import PathIsh, Paths, dataclass


@dataclass
class config(user_config):
    # path[s]/glob to the backed up ttt history files
    # (can be a list if you want to provide the live file)
    export_path: Paths


import csv
from pathlib import Path
from typing import Sequence

from my.core import get_files, warn_if_empty, Stats
from .utils.time import parse_datetime_sec
from .utils.common import InputSource


def inputs() -> Sequence[Path]:
    return get_files(config.export_path)


from datetime import datetime
from typing import NamedTuple, Iterator, Set, Tuple
from itertools import chain


# represents one history entry (command)
class Entry(NamedTuple):
    dt: datetime
    command: str
    directory: Optional[str]


Results = Iterator[Entry]


def history(from_paths: InputSource = inputs) -> Results:
    yield from _merge_histories(*map(_parse_file, from_paths()))


@warn_if_empty
def _merge_histories(*sources: Results) -> Results:
    emitted: Set[Tuple[datetime, str]] = set()
    for e in chain(*sources):
        key = (e.dt, e.command)
        if key in emitted:
            # logger.debug('ignoring %s: %s', key, e)
            continue
        yield e
        emitted.add(key)


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
