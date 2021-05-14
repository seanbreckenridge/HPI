"""
Parses bash history (mostly from servers/vps I run)
using the following bootstrap script:
https://github.com/seanbreckenridge/bootstrap/

This parses the histories with the following configuration:

export HISTTIMEFORMAT="%s "
export HISTFILESIZE=-1
export HISTSIZE=-1
export HISTCONTROL=ignoredups
export HISTIGNORE=?:??
shopt -s histappend  # dont overwrite history
shopt -s cmdhist   # save al-lines of multi-line commands in the same entry
shopt -s lithist  # embedded newlines for multi-line commands

That adds timestamps to history, making it look like:

#1620931766
command ls
#1620931767
command ls -al
#1620931737
which ls
"""

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import bash as user_config  # type: ignore[attr-defined]
from my.core import Paths, dataclass


@dataclass
class config(user_config):
    # path[s]/glob to the exported bash history files
    export_path: Paths


from pathlib import Path
from typing import Sequence, List
from datetime import datetime
from typing import NamedTuple, Iterator, Set, Tuple
from itertools import chain

from my.core import get_files, warn_if_empty, Stats, LazyLogger
from my.core.common import mcachew
from .utils.time import parse_datetime_sec
from .utils.common import InputSource


logger = LazyLogger(__name__, level="warning")


def inputs() -> Sequence[Path]:
    return get_files(config.export_path)


# represents one history entry (command)
class Entry(NamedTuple):
    dt: datetime
    command: str


Results = Iterator[Entry]


def _cachew_depends_on(for_paths: InputSource = inputs) -> List[float]:
    return [p.stat().st_mtime for p in for_paths()]


@mcachew(depends_on=_cachew_depends_on, logger=logger)
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
    dt = None
    command_buf = ""  # current command
    for line in histfile.open(encoding="latin-1"):
        if line.startswith("#"):
            # parse lines like '#1620931766'
            # possible string datetime
            sdt = line[1:].strip()  # remove newline
            try:
                newdt = parse_datetime_sec(sdt)
            except Exception as e:
                logger.debug(f"Error while parsing datetime {e}")
            else:
                # this case happens when we successfully parse a datetime line
                # yield old data, then set newly parsed data to next items datetime
                if dt is not None:
                    # rstrip \n gets rid of the last newline for a command, if
                    # there were multiple lines
                    yield Entry(dt=dt, command=command_buf.rstrip("\n"))
                # set new datetime for next entry
                dt = newdt
                # overwrite command buffer
                command_buf = ""
                continue
        # otherwise, append. this already includes newline
        command_buf += line
    # yield final command
    if dt is not None and command_buf.strip():
        yield Entry(dt=dt, command=command_buf.rstrip("\n"))


def stats() -> Stats:
    from my.core import stat

    return {**stat(history)}
