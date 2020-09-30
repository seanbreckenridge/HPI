"""
Parses history from https://github.com/seanbreckenridge/ttt
"""

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import ttt as user_config  # type: ignore

from dataclasses import dataclass
from typing import Optional

from .core import PathIsh, Paths


@dataclass
class ttt(user_config):
    # path[s]/glob to the backed up ttt history files
    export_path: Paths

    # path to current ttt history (i.e. the live file)
    live_file: Optional[PathIsh] = None


from .core.cfg import make_config

config = make_config(ttt)

#######

import csv
import warnings
from pathlib import Path
from typing import Sequence

from .core import get_files, warn_if_empty
from .core.common import listify
from .core.time import parse_datetime_sec


@listify
def inputs() -> Sequence[Path]:  # type: ignore
    """
    Returns all inputs, including live_file if provided and backups
    """
    yield from get_files(config.export_path)
    if config.live_file is not None:
        p: Path = Path(config.live_file).expanduser().absolute()
        if p.exists():
            yield p
        else:
            warnings.warn(
                f"'live_file' provided {config.live_file} but that file doesn't exist."
            )


from datetime import datetime
from typing import NamedTuple, Iterator, Set, Tuple
from itertools import chain


# represents one history entry (command)
class Entry(NamedTuple):
    dt: datetime
    command: str
    directory: Optional[str]


Results = Iterator[Entry]


def history(from_paths=inputs) -> Results:
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


def stats():
    from .core import stat

    return {**stat(history)}
