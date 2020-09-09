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


# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import ipython as user_config  # type: ignore

from dataclasses import dataclass

from .core import Paths


@dataclass
class ipython(user_config):
    # path[s]/glob to the exported ipython sqlite databases
    export_path: Paths


from .core.cfg import make_config

config = make_config(ipython)


from datetime import datetime
from typing import Iterator, NamedTuple, Sequence, Callable, List
from itertools import chain

from IPython.core.history import HistoryAccessor

from .core import get_files, warn_if_empty
from .core.common import listify


class Command(NamedTuple):
    at: datetime
    command: str


Results = Iterator[Command]


# Return backed up sqlite databases
@listify
def inputs() -> Sequence[str]:  # type: ignore
    yield from map(str, get_files(config.export_path))
    # the empty string makes IPython use the live history file ~/.local/share/ipython/.../history.sqlite
    # instead of one of the files from the export backup
    # merge histories combines those
    yield ""


def history(from_paths: Callable[[None], List[Sequence[str]]] = inputs) -> Results:
    yield from _merge_histories(*from_paths())  # type: ignore


@warn_if_empty
def _merge_histories(*sources: Sequence[str]) -> Results:
    yield from set(chain(*map(_parse_database, sources)))  # type: ignore


def _parse_database(sqlite_database: str = "") -> Results:
    """
    If empty string is provided as sqlite database, uses the live ipython database file instead
    """
    hist = HistoryAccessor(hist_file=sqlite_database)
    total_sessions = hist.get_last_session_id()
    for sess in range(1, total_sessions):
        session_info = hist.get_session_info(
            sess
        )  # get when this session started, use that as timestamp
        assert len(session_info) == 5  # sanity checks
        start_time = session_info[1]
        assert isinstance(start_time, datetime)
        for msg in hist.get_range(sess).fetchall():  # sqlite cursor
            assert len(msg) == 3
            assert isinstance(msg[-1], str)
            yield Command(command=msg[-1], at=start_time)


def stats():
    from .core import stat

    return {**stat(history)}
