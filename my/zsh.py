"""
Parses ZSH history (uses exports from ./job/zsh_history.job) and current zsh history (from $ZDOTDIR)
"""

# if on multiple computers, the zsh histories can be copied into the zsh.export_path
# and it will merge everything without duplicates

# look at https://github.com/bamos/zsh-history-analysis

from typing import Optional

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import zsh as user_config  # type: ignore[attr-defined]
from my.core import PathIsh, Paths, dataclass


@dataclass
class config(user_config):
    # path[s]/glob to the exported zsh history files
    export_path: Paths

    # path to current zsh history (i.e. the live file)
    live_file: Optional[PathIsh]


from pathlib import Path
from typing import Sequence
from functools import lru_cache

from my.core import get_files, warn_if_empty, Stats, LazyLogger
from my.core.common import mcachew
from my.core.warnings import low
from .utils.time import parse_datetime_sec
from .utils.common import InputSource


logger = LazyLogger(__name__, level="warning")


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
        # dont ned to spend the time doing the additional _merge_histories
        yield from _history_from_backups(from_paths)


@mcachew(depends_on=lambda p: list(sorted(p())), logger=logger)
def _history_from_backups(from_paths: InputSource) -> Results:
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


def stats() -> Stats:
    from my.core import stat

    return {**stat(history)}
