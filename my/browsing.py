"""
Parses Firefox History using http://github.com/seanbreckenridge/ffexport
"""

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

from my.core import Stats, get_files
from my.core.common import listify


# monkey patch ffexport logs
if "HPI_LOGS" in os.environ:
    from logzero import setup_logger  # type: ignore[import]
    from my.core.logging import mklevel
    import ffexport.log

    ffexport.log.logger = setup_logger(
        name="ffexport", level=mklevel(os.environ["HPI_LOGS"])
    )


from ffexport import read_and_merge, Visit
from ffexport.save_hist import backup_history


@listify
def inputs(tmp_dir: Optional[str] = None) -> Sequence[Path]:  # type: ignore[misc]
    """
    Returns all inputs, including old sqlite backups (from config.export_path) and the current firefox history
    """
    yield from get_files(config.export_path)
    # get the live file from ~/.mozilla/.... (see ffexport.save_hist)
    # warning: could run out of space on /tmp if your computer is up *forever*, or youre running pytest a bunch
    if tmp_dir is None:
        tmp_dir = tempfile.mkdtemp()
    # I only use the one profile, so profile defaults to *
    backup_history(browser="firefox", to=Path(tmp_dir))
    live_copy: Sequence[Path] = get_files(tmp_dir, glob="*.sqlite")
    assert len(live_copy) >= 1, f"Couldn't find live history backup in {tmp_dir}"
    yield sorted(live_copy, key=lambda p: p.stat().st_mtime)[-1]


Results = Iterator[Visit]


def history(from_paths=inputs, tmp_dir: Optional[str] = None) -> Results:
    """
    used like:
    import my.browsing
    visits = list(my.browsing.history())
    """
    if hash(from_paths) == hash(inputs):
        yield from read_and_merge(*from_paths(tmp_dir=tmp_dir))
    else:
        yield from read_and_merge(*from_paths())


def stats() -> Stats:
    from my.core import stat

    return {**stat(history)}
