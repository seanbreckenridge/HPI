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
import tempfile
from pathlib import Path
from typing import Iterator, Sequence, Optional

from my.core import Stats, get_files, LazyLogger
from my.core.common import mcachew


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
from ffexport.save_hist import backup_history


def backup_inputs() -> Sequence[Path]:
    """Returns all backed up ffexport databases"""
    return list(get_files(config.export_path))


def _copy_live_database(tmp_dir: Optional[str] = None) -> Path:
    # get the live file from ~/.mozilla/.... (see ffexport.save_hist)
    # warning: could run out of space on /tmp if your computer is up *forever*, or youre running pytest a bunch
    if tmp_dir is None:
        tmp_dir = tempfile.mkdtemp()
    # I only use the one profile, so profile defaults to *
    backup_history(browser="firefox", to=Path(tmp_dir))
    live_copy: Sequence[Path] = get_files(tmp_dir, glob="*.sqlite")
    assert len(live_copy) == 1, f"Couldn't find live history backup in {tmp_dir}"
    return live_copy[0]


Results = Iterator[Visit]


# don't put this behind cachew, since the history database
# is constantly copied when this is called, so the path is different/
# there may be new visits from the active firefox browser
def history(tmp_dir: Optional[str] = None) -> Results:
    live_visits: Results = read_visits(_copy_live_database(tmp_dir))
    yield from merge_visits(_history_from_backups(), live_visits)


@mcachew(depends_on=lambda: sorted(map(str, backup_inputs())), logger=logger)
def _history_from_backups() -> Results:
    # not sure how to type this properly?
    yield from read_and_merge(*backup_inputs())  # type: ignore[arg-type]


def stats() -> Stats:
    from my.core import stat

    return {**stat(history)}
