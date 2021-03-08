"""
Parses history from https://github.com/seanbreckenridge/aw-watcher-window
"""

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import window_watcher as user_config

from dataclasses import dataclass
from typing import Optional, List

from .core import PathIsh, Paths


@dataclass
class window_watcher(user_config):
    # path[s]/glob to the backed up window_watcher history files
    export_path: Paths

    # force individual events for these applications
    force_individual: Optional[List[str]] = None

    # path to current window_watcher history (i.e. the live file)
    live_file: Optional[PathIsh] = None


from .core.cfg import make_config

config = make_config(window_watcher)

#######

import csv
import warnings
from io import StringIO
from pathlib import Path
from datetime import datetime, timedelta
from typing import NamedTuple, Iterator, Tuple, Dict, Set, Sequence
from itertools import chain

from .core import get_files, warn_if_empty, Stats
from .core.common import listify
from .core.time import parse_datetime_sec
from .core.file import filter_subfile_matches


@listify
def inputs() -> Sequence[Path]:  # type: ignore[misc]
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


# represents one history entry
class LinearResult(NamedTuple):
    dt: datetime
    duration: int
    application: str
    window_title: str


DurInfo = List[Tuple[datetime, timedelta]]

# start_time does duplicate
class Result(NamedTuple):
    start_time: datetime
    times: DurInfo
    application: str
    window_title: str


Results = Iterator[Result]
LinearResults = Iterator[LinearResult]


def history(from_paths=inputs) -> Results:
    yield from _construct_stream(
        filter(
            _is_unlikely,
            _merge_histories(*map(_parse_file, filter_subfile_matches(from_paths()))),
        )
    )


def _construct_stream(
    res: LinearResults, exit_when: timedelta = timedelta(hours=2)
) -> Results:
    """
    exit_when describes when an item should exit recent_cache
    """
    recent_cache: Dict[Tuple[str, str], DurInfo] = {}
    fset: Set[str] = set(config.force_individual)
    exit_secs = int(exit_when.total_seconds())
    for item in res:
        key: Tuple[str, str] = (item.application, item.window_title)
        # if should be forced individual
        if item.application in fset:
            yield Result(
                start_time=item.dt,
                times=[(item.dt, timedelta(seconds=item.duration))],
                application=item.application,
                window_title=item.window_title,
            )
            continue
        if key in recent_cache:
            # exit if more than 2 hours ago
            val: DurInfo = recent_cache[key]
            (lval, ldur) = val[-1]
            # when this 'row' ended
            lend: datetime = lval + ldur
            if item.dt.timestamp() - lend.timestamp() > exit_secs:
                val = recent_cache.pop(key)
                yield Result(
                    start_time=val[0][0],
                    times=val,
                    application=item.application,
                    window_title=item.window_title,
                )
                # re-add this item to cache
                recent_cache[key] = [(item.dt, timedelta(seconds=item.duration))]
            else:
                val.append((item.dt, timedelta(seconds=item.duration)))
        else:
            # key not in cache
            recent_cache[key] = [(item.dt, timedelta(seconds=item.duration))]
    for (appname, window_title), val in recent_cache.items():
        yield Result(
            start_time=val[0][0],
            times=val,
            application=appname,
            window_title=window_title,
        )


@warn_if_empty
def _merge_histories(*sources: LinearResults) -> LinearResults:
    emitted: Set[datetime] = set()
    for e in chain(*sources):
        key = e.dt
        if key in emitted:
            # print('ignoring %s: %s', key, e)
            continue
        yield e
        emitted.add(key)


unlikely_duration: int = 3600
for_applications: Set[str] = set(["firefoxdeveloperedition", "Alacritty"])

very_unlikely_duration: int = unlikely_duration * 2


# this probably didnt happen, was either 'unknown' or me leaving
# a tab open for a *long* time while AFK
def _is_unlikely(e: LinearResult) -> bool:
    if e.window_title == "unknown" and e.application == "unknown":
        return False
    if e.duration > very_unlikely_duration:
        return False
    if e.duration > unlikely_duration and e.application in for_applications:
        return False
    return True


def _parse_file(histfile: Path) -> LinearResults:
    with histfile.open("r", encoding="utf-8", newline="") as f:
        contents = f.read()
    # convert line breaks to unix style; i.e. broken ^M characters
    buf = StringIO(contents.replace("\r", ""))
    csv_reader = csv.reader(
        buf, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
    )
    while True:
        try:
            row = next(csv_reader)
            yield LinearResult(
                dt=parse_datetime_sec(row[0]),
                duration=int(row[1]),
                application=row[2],
                window_title=row[3],
            )
        except csv.Error:
            # some lines contain the NUL byte for some reason... ??
            # seems to be x-lib/encoding errors causing malformed application/file names
            # catch those and ignore them
            pass
        except StopIteration:
            return


def stats() -> Stats:
    from .core import stat

    return {**stat(history)}
