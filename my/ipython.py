"""
Get IPython (REPL) History with datetimes
https://ipython.readthedocs.io/en/stable/api/generated/IPython.core.history.html?highlight=hist#IPython.core.history.HistoryAccessor.__init__

In order to save python history with timestamps, I define the following in my zshrc:

# if I type python with out any arguments, launch ipython instead
python() { python3 "$@" }
python3() {
  if (( $# == 0 )); then
    echo -e "$(tput setaf 2)Launching ipython instead...$(tput sgr0)"
    ipython
  else
    /usr/bin/python3 "$@"
  fi
}
"""

REQUIRES = ["ipython>=8.5.0"]


# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import ipython as user_config  # type: ignore[attr-defined]

from my.core import Paths, dataclass


@dataclass
class config(user_config):
    # path[s]/glob to the exported ipython sqlite databases
    export_path: Paths


from pathlib import Path
from datetime import datetime
from typing import Iterable, NamedTuple, Iterator, Optional
from itertools import chain

from more_itertools import unique_everseen
from IPython.core.history import HistoryAccessor

from my.core import get_files, Stats, LazyLogger
from my.utils.input_source import InputSource

logger = LazyLogger(__name__)


class Command(NamedTuple):
    dt: datetime
    command: str


Results = Iterator[Command]


# Return backed up sqlite databases
def inputs() -> Iterable[Path]:
    yield from get_files(config.export_path)


def _live_history() -> Results:
    # the empty string makes IPython use the live history file ~/.local/share/ipython/.../history.sqlite
    # instead of one of the files from the export backup
    # merge histories combines those
    #
    # seems that this has the possibility to fail to locate your live
    # history file if its being run in the background? unsure why
    try:
        yield from _parse_database(sqlite_database="")
    except Exception as e:
        logger.warning(f"Failed to get data from current ipython database: {e}")
        return


def history(from_paths: InputSource = inputs) -> Results:
    yield from unique_everseen(
        chain(*(_parse_database(str(p)) for p in from_paths()), _live_history()),
        key=lambda h: (h.command, h.dt),
    )


def _parse_database(sqlite_database: str) -> Results:
    hist = HistoryAccessor(hist_file=sqlite_database)  # type: ignore[no-untyped-call]
    try:
        total_sessions: Optional[int] = hist.get_last_session_id()
    except Exception as e:
        logger.warning(f"Failed to get last session id: {e}")
        # if database is corrupt/fails to compute sessions, skip
        return
    if total_sessions is None:
        return
    # yes, these start at 1
    for sess in range(1, total_sessions + 1):
        # get when this session started, use that as timestamp
        session_info = hist.get_session_info(sess)
        assert len(session_info) == 5  # sanity checks
        start_time = session_info[1]
        assert isinstance(start_time, datetime)
        for msg in hist.get_range(sess).fetchall():  # sqlite cursor
            assert len(msg) == 3
            assert isinstance(msg[-1], str)
            yield Command(command=msg[-1], dt=start_time)


def stats() -> Stats:
    from my.core import stat

    return {**stat(history)}
