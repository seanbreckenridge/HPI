"""
Parses Firefox History using http://github.com/seanbreckenridge/ffexport
"""

REQUIRES = ["ffexport"]

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import firefox as user_config  # type: ignore[attr-defined]

from my.core import Paths, dataclass


@dataclass
class config(user_config):
    # path[s]/glob to the exported firefox history sqlite files
    export_path: Paths


import os
from pathlib import Path
from typing import Iterator, Sequence, List

from my.core import Stats, get_files, LazyLogger
from my.core.common import mcachew
from my.core.sqlite import sqlite_copy_and_open


# monkey patch ffexport logs
if "HPI_LOGS" in os.environ:
    from logzero import setup_logger  # type: ignore[import]
    from my.core.logging import mklevel
    import ffexport.log

    ffexport.log.logger = setup_logger(
        name="ffexport", level=mklevel(os.environ["HPI_LOGS"])
    )

# not the ffexport logger, used for cachew info
logger = LazyLogger(__name__, level="warning")


from ffexport import read_and_merge, Visit
from ffexport.merge_db import merge_visits, read_visits
from ffexport.save_hist import get_path


def backup_inputs() -> Sequence[Path]:
    """Returns all backed up ffexport databases"""
    return list(get_files(config.export_path))


# return the visits from the live sqlite database, copying the live database in memory
def _live_visits() -> List[Visit]:
    live_db: Path = get_path(browser="firefox")
    conn = sqlite_copy_and_open(live_db)
    try:
        # consume generator early, so the connection doesn't close before we read the visits
        return list(read_visits(conn))
    finally:
        conn.close()


Results = Iterator[Visit]


# don't put this behind cachew, since the history database
# is constantly copied when this is called, so the path is different/
# there may be new visits from the active firefox browser
def history() -> Results:
    yield from merge_visits(_history_from_backups(), iter(_live_visits()))


@mcachew(depends_on=lambda: sorted(map(str, backup_inputs())), logger=logger)
def _history_from_backups() -> Results:
    # hmm... not sure how to type this properly?
    yield from read_and_merge(*backup_inputs())  # type: ignore[arg-type]


def stats() -> Stats:
    from my.core import stat

    return {**stat(history)}
