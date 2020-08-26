"""
Parses ZSH history (uses exports from ./job/zsh_history.job) and current zsh history (from $ZDOTDIR)
"""

# if on multiple computers, the zsh histories can be copied into the zsh.export_path
# and it will merge everything without duplicates

# look at https://github.com/bamos/zsh-history-analysis

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import zsh as user_config  # type: ignore

from dataclasses import dataclass
from typing import Optional

from .core import PathIsh, Paths


@dataclass
class zsh(user_config):
    # path[s]/glob to the exported zsh history files
    export_path: Paths

    # path to current zsh history (i.e. the live file)
    live_zsh_history: Optional[PathIsh] = None


from .core.cfg import make_config

config = make_config(zsh)

#######

import warnings
from pathlib import Path
from typing import Sequence

from .core import get_files, warn_if_empty
from .core.common import listify


@listify
def inputs() -> Sequence[Path]:
    """
    Returns all inputs, including live_zsh_history if provided and exported histories
    """
    yield from get_files(config.export_path, glob="*.zsh")
    if config.live_zsh_history is not None:
        p: Path = Path(config.live_zsh_history).expanduser().absolute()
        if p.exists():
            yield p
        else:
            warnings.warn(
                f"'live_zsh_history' provided {config.live_zsh_history} but that file doesn't exist."
            )


### This parses the zsh format I've configured, zsh is heavily configurable
### Mine looks like:
### : 1598471925:470;python3
### : datetime:duration:command
### See here for zsh configuration I've set
### https://github.com/seanbreckenridge/dotfiles/blob/95f1869632e6c0d72fb5fbf901f0dacddbbd1043/.config/zsh/env_config.zsh#L9-L18

import re
import io

from datetime import datetime, timedelta
from typing import NamedTuple, Iterable, Iterator, Set, Tuple

from .core.error import Res

# represent command length
duration = timedelta

from .kython.klogging import LazyLogger
logger = LazyLogger(__name__)

# represents one history entry
class Entry(NamedTuple):
    dt: datetime
    duration: duration
    command: str


Results = Iterable[Res[Entry]]


def history(from_paths=inputs):
    yield from _merge_histories(*map(_parse_file, from_paths()))


@warn_if_empty
def _merge_histories(*sources: Results) -> Results:

    from itertools import chain

    emitted: Set[Tuple[datetime, str]] = set()
    for e in chain(*sources):
        if isinstance(e, Exception):
            yield e
            continue

        # replace spaces and slashes and strip command
        # this is just to make the (dt, commandstr) pair more likely
        # to remove duplicates and be unique
        # the command from the event is emitted without any changes
        key = (e.dt, e.command)
        if key in emitted:
            # logger.debug('ignoring %s: %s', key, e)
            continue
        yield e
        emitted.add(key)


# TODO: maybe cachew? sort of interferes with the live_zsh_history exports
# if this gets to slow in the future, better solution would probably be to
# pre-emptively read files in, check if ones a substring of another and
# exclude it
def _parse_file(histfile: Path) -> Results:
    dt, dur, command = None, None, ""
    # cant parse line by line since some commands are multiline
    # sort of structured like a do-while loop
    for line in _yield_lines(histfile):
        r = _parse_metadata(line)
        # if regex didnt match, this is a multi line command string
        if r is None:
            command += "\n" + line
        else:
            # this 'if' is needed for the first item (since its not set on the first loop)
            # yield the last command
            if dt:
                yield Entry(
                    dt=_parse_datetime(dt),
                    duration=_parse_duration(dur),
                    command=command.strip(),
                )
            # set 'current' dt, dur, command to matched groups
            dt, dur, command = r
    # yield the last entry
    if command.strip() != "":
        yield Entry(
            dt=_parse_datetime(dt), duration=_parse_duration(dur), command=command.strip()
        )


def _parse_metadata(histline: str) -> Optional[Iterable[str]]:
    """
    parse the date, duration, and command from a line
    """
    matches = re.match(r"^: (\d+):(\d+);(.*)$", histline)
    if not bool(matches):
        return None
    else:
        return list(matches.groups())


def _parse_datetime(date: Optional[str]) -> datetime:
    if date is None:
        logger.warning(f"_parse_datetime receieved {date}, expected a datetime")
        return datetime.now()
    else:
        return datetime.utcfromtimestamp(int(date),)


def _parse_duration(dur: Optional[str]) -> duration:
    if dur is None:
        logger.warning(f"_parse_duration receieved {dur}, expected a string")
        return duration(seconds=0)
    else:
        return duration(seconds=int(dur))


def _yield_lines(histfile: Path) -> Iterator[str]:
    with io.open(histfile, encoding="latin-1") as hist_f:
        for line in hist_f:
            if line.strip() == "":
                continue
            yield line


