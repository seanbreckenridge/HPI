"""
Parses history from https://github.com/seanbreckenridge/aw-watcher-window
"""

REQUIRES = ["git+https://github.com/seanbreckenridge/aw-watcher-window"]

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import window_watcher as user_config  # type: ignore[attr-defined]

import csv
from io import StringIO
from pathlib import Path
from datetime import datetime, timedelta
from typing import NamedTuple, Iterator, Tuple, Dict, Set, Sequence, Optional, List
from itertools import chain

from my.core import get_files, Stats, Paths, dataclass
from my.utils.time import parse_datetime_sec
from my.utils.input_source import InputSource

from more_itertools import unique_everseen


@dataclass
class config(user_config):
    # path[s]/glob to the backed up window_watcher history files
    export_path: Paths

    # force individual events for these applications
    force_individual: Optional[List[str]] = None


def inputs() -> Sequence[Path]:
    return get_files(config.export_path)


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


def history(from_paths: InputSource = inputs) -> Results:
    yield from _construct_stream(
        filter(
            _is_unlikely,
            unique_everseen(chain(*map(_parse_file, from_paths())), key=lambda e: e.dt),
        )
    )


def _construct_stream(
    res: LinearResults, exit_when: timedelta = timedelta(hours=6)
) -> Results:
    """
    Combines a bunch of individual events into groups. I.e.
    if I had one webpage I switched back and forth from for
    a few hours, it combines all those LinearResults into
    one, listing the timestamps/duration for each visit.

    exit_when describes when an item should exit recent_cache
    """

    # uses the [application, window_title] tuple as the key
    recent_cache: Dict[Tuple[str, str], DurInfo] = {}
    fset: Set[str] = set(config.force_individual or [])
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
            # exit if more than 6 hours ago
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
                # item was ejected from cache because its been too long, add this item into the cache
                recent_cache[key] = [(item.dt, timedelta(seconds=item.duration))]
            else:
                val.append((item.dt, timedelta(seconds=item.duration)))
        else:
            # key not in cache
            recent_cache[key] = [(item.dt, timedelta(seconds=item.duration))]
    # yield all the leftover items from cache
    for (appname, window_title), val in recent_cache.items():
        yield Result(
            start_time=val[0][0],
            times=val,
            application=appname,
            window_title=window_title,
        )


unlikely_duration: int = 3600
for_applications: Set[str] = set(["firefoxdeveloperedition", "firefox", "Alacritty"])

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
    from my.core import stat

    return {**stat(history)}
