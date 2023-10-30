"""
Parses ZSH history (uses exports from ./job/zsh_history.job) and current zsh history (from $ZDOTDIR)

This parses the zsh format I've configured, zsh is heavily configurable
Mine looks like:
: 1598471925:470;python3
: datetime:duration:command

My config looks like:

HISTFILE="${ZDOTDIR}/.zsh_history"
HISTSIZE=1000000
SAVEHIST=1000000
setopt APPEND_HISTORY     # append to history file instead of replacing
setopt HIST_REDUCE_BLANKS # delete empty lines from history file
setopt HIST_IGNORE_SPACE  # ignore lines that start with space
setopt HIST_NO_STORE      # Do not add history and fc commands to the history
setopt EXTENDED_HISTORY   # save time/duration to history file
"""

# if on multiple computers, the zsh histories can be copied into the zsh.export_path
# and it will merge everything without duplicates

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import zsh as user_config  # type: ignore[attr-defined]

from pathlib import Path
from typing import Sequence, Optional
from functools import lru_cache

from my.core import (
    get_files,
    warn_if_empty,
    Stats,
    make_logger,
    PathIsh,
    Paths,
    dataclass,
)
from my.core.common import mcachew
from my.core.warnings import low
from my.utils.time import parse_datetime_sec
from my.utils.input_source import InputSource

from more_itertools import unique_everseen


@dataclass
class config(user_config):
    # path[s]/glob to the exported zsh history files
    export_path: Paths

    # path to current zsh history (i.e. the live file)
    live_file: Optional[PathIsh]


logger = make_logger(__name__)


def backup_inputs() -> Sequence[Path]:
    return list(get_files(config.export_path))


@lru_cache(1)
def _live_file() -> Optional[Path]:
    if config.live_file is not None:
        p: Path = Path(config.live_file).expanduser().absolute()
        if p.exists():
            return p
        else:
            low(f"'live_file' provided {config.live_file} but that file doesn't exist.")
            return None
    return None


import re

from datetime import datetime
from typing import NamedTuple, Iterator, Tuple
from itertools import chain


# represents one history entry (command)
class Entry(NamedTuple):
    dt: datetime
    duration: int
    command: str


Results = Iterator[Entry]


def history(from_paths: InputSource = backup_inputs) -> Results:
    # if user has specified some other function as input
    if hash(from_paths) != hash(backup_inputs):
        yield from _merge_histories(*map(_parse_file, from_paths()))
        return
    lf = _live_file()
    if lf is not None:
        yield from _merge_histories(_history_from_backups(from_paths), _parse_file(lf))
    else:
        # if we're not merging the live history file
        # dont need to spend the time doing the additional _merge_histories
        yield from _history_from_backups(from_paths)


def _depends_on(p: InputSource) -> Sequence[Path]:
    return sorted(p())


@mcachew(depends_on=_depends_on, logger=logger)
def _history_from_backups(from_paths: InputSource) -> Results:
    yield from _merge_histories(*map(_parse_file, from_paths()))


@warn_if_empty
def _merge_histories(*sources: Results) -> Results:
    yield from unique_everseen(
        chain(*sources),
        key=lambda e: (
            e.dt,
            e.command,
        ),
    )


def _parse_file(histfile: Path) -> Results:
    dt: Optional[datetime] = None
    dur: Optional[int] = None
    command: str = ""
    # can't parse line by line since some commands are multiline
    # sort of structured like a do-while loop
    for line in histfile.open(encoding="latin-1"):
        r = _parse_metadata(line)
        # if regex didn't match, this is a multi line command string
        if r is None:
            command += "\n" + line
        else:
            # this 'if' is needed for the first item (since its not set on the first loop)
            # yield the last command
            if dt is not None and dur is not None:
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


def stats() -> Stats:
    from my.core import stat

    return {**stat(history)}
