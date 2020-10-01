"""
Parses ZSH history (uses exports from ./job/zsh_history.job) and current zsh history (from $ZDOTDIR)
"""

# if on multiple computers, the zsh histories can be copied into the zsh.export_path
# and it will merge everything without duplicates
# note: the first 100 lines of the zsh history should be different (even if only by one line), since this
# removes duplicate histories by matching the first 100 lines (see filter_inputs below)

# look at https://github.com/bamos/zsh-history-analysis

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import zsh as user_config

from dataclasses import dataclass
from typing import Optional

from .core import PathIsh, Paths


@dataclass
class zsh(user_config):
    # path[s]/glob to the exported zsh history files
    export_path: Paths

    # path to current zsh history (i.e. the live file)
    live_file: Optional[PathIsh] = None


from .core.cfg import make_config

config = make_config(zsh)

#######

import warnings
from pathlib import Path
from typing import Sequence

from .core import get_files, warn_if_empty
from .core.common import listify
from .core.time import parse_datetime_sec
from .core.file import filter_subfile_matches


@listify
def inputs() -> Sequence[Path]:  # type: ignore[misc]
    """
    Returns all inputs, including live_file if provided and exported histories
    """
    yield from get_files(config.export_path, glob="*.zsh")
    if config.live_file is not None:
        p: Path = Path(config.live_file).expanduser().absolute()
        if p.exists():
            yield p
        else:
            warnings.warn(
                f"'live_file' provided {config.live_file} but that file doesn't exist."
            )


### This parses the zsh format I've configured, zsh is heavily configurable
### Mine looks like:
### : 1598471925:470;python3
### : datetime:duration:command
### See here for zsh configuration I've set
### https://github.com/seanbreckenridge/dotfiles/blob/95f1869632e6c0d72fb5fbf901f0dacddbbd1043/.config/zsh/env_config.zsh#L9-L18

import re

from datetime import datetime
from typing import NamedTuple, Iterator, Set, Tuple
from itertools import chain


# represents one history entry (command)
class Entry(NamedTuple):
    dt: datetime
    duration: int
    command: str


Results = Iterator[Entry]


def history(from_paths=inputs) -> Results:
    yield from _merge_histories(*map(_parse_file, filter_subfile_matches(from_paths())))


def stats():
    from .core import stat

    return {**stat(history)}


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
    dt, dur, command = None, None, ""
    # cant parse line by line since some commands are multiline
    # sort of structured like a do-while loop
    for line in histfile.open(encoding="latin-1"):
        r = _parse_metadata(line)
        # if regex didnt match, this is a multi line command string
        if r is None:
            command += "\n" + line
        else:
            # this 'if' is needed for the first item (since its not set on the first loop)
            # yield the last command
            if dur is not None:
                yield Entry(
                    dt=dt,
                    duration=dur,
                    command=command,
                )
            # set 'current' dt, dur, command to matched groups
            dt, dur, command = r
    # yield the last entry
    if command:
        yield Entry(
            dt=dt,  # type: ignore[arg-type]
            duration=dur,  # type: ignore[arg-type]
            command=command,
        )


PATTERN = re.compile(r"^: (\d+):(\d+);(.*)$")


def _parse_metadata(histline: str) -> Optional[Tuple[datetime, int, str]]:
    """
    parse the date, duration, and command from a line
    """
    matches = PATTERN.match(histline)
    if matches:
        g = matches.groups()
        return (parse_datetime_sec(g[0]), int(g[1]), g[2])
    return None
