"""
Parses Browser history using
http://github.com/seanbreckenridge/browserexport
"""

REQUIRES = ["git+https://github.com/seanbreckenridge/browserexport"]

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import browsing as user_config  # type: ignore[attr-defined]

from my.core import Paths, dataclass


@dataclass
class config(user_config):
    # path[s]/glob to your backed-up sqlite history files
    export_path: Paths

    # paths to the sqlite database files which you
    # use frequently, which should be combined into your history
    # makes sure this grabs your most recent history if it
    # hasn't been backed up yet
    # see my link above to my config above for an example
    live_databases: Paths


import os
from pathlib import Path
from typing import Iterator, List

from my.core import Stats, get_files, LazyLogger
from my.core.common import mcachew
from my.core.sqlite import sqlite_copy_and_open


# patch browserexport logs if HPI_LOGS is present
if "HPI_LOGS" in os.environ:
    from browserexport.log import setup as setup_browserexport_logger
    from my.core.logging import mklevel

    setup_browserexport_logger(mklevel(os.environ["HPI_LOGS"]))

logger = LazyLogger(__name__, level="warning")


from browserexport.merge import read_and_merge, merge_visits, Visit
from browserexport.parse import read_visits


# all of my backed up databases
def backup_inputs() -> List[Path]:
    return list(get_files(config.export_path))


# return the visits from the live sqlite database,
# copying the live database in memory
def _live_visits() -> List[Visit]:
    visits: List[Visit] = []
    live_dbs = get_files(config.live_databases or "")
    logger.debug(f"Live databases: {live_dbs}")
    for live_db in live_dbs:
        conn = sqlite_copy_and_open(live_db)
        try:
            # consume generator early,
            # so the connection doesn't close before we read the visits
            visits.extend(list(read_visits(conn)))
        finally:
            conn.close()
    logger.debug(f"Read {len(visits)} live visits")
    return visits


Results = Iterator[Visit]


# don't put this behind cachew, since the history database
# is constantly copied when this is called, so the path is different/
# there may be new visits from the active sqlite datbases
def history() -> Results:
    yield from merge_visits([_history_from_backups(), iter(_live_visits())])


@mcachew(depends_on=lambda: sorted(map(str, backup_inputs())), logger=logger)
def _history_from_backups() -> Results:
    yield from read_and_merge(backup_inputs())


def stats() -> Stats:
    from my.core import stat

    return {**stat(history)}
