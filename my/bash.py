"""
Parses bash history (mostly from servers/vps I run)
using the following bootstrap script:
https://github.com/seanbreckenridge/bootstrap/

This parses bash history with the following configuration:

export HISTTIMEFORMAT="%s "
export HISTFILESIZE=-1
export HISTSIZE=-1
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

from pathlib import Path
from typing import Sequence, List
from datetime import datetime
from typing import NamedTuple, Iterator, Optional
from itertools import chain

from more_itertools import unique_everseen

from my.core import get_files, Stats, LazyLogger, Paths, dataclass
from my.core.common import mcachew
from my.utils.time import parse_datetime_sec
from my.utils.input_source import InputSource


@dataclass
class config(user_config):
    # path[s]/glob to the exported bash history files
    export_path: Paths


logger = LazyLogger(__name__)


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
    yield from unique_everseen(
        chain(*map(_parse_file, from_paths())),
        key=lambda h: (
            h.dt,
            h.command,
        ),
    )


def _parse_file(histfile: Path) -> Results:
    dt: Optional[datetime] = None
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
                    # rstrip \n gets rid of the last newline for each command
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
