"""
Parses Firefox History using http://github.com/seanbreckenridge/ffexport
"""

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import firefox as user_config  # type: ignore

from dataclasses import dataclass

from .core import Paths


@dataclass
class firefox(user_config):
    # path[s]/glob to the exported firefox history sqlite files
    export_path: Paths

from .core.cfg import make_config
config = make_config(firefox)

#######

import tempfile
from pathlib import Path
from typing import Iterator, Sequence

from .core.common import listify, get_files

from ffexport import read_and_merge, Visit
from ffexport.save_hist import backup_history


@listify
def inputs() -> Sequence[Path]:
    """
    Returns all inputs, including old sqlite backups (from config.export_path) and the current firefox history
    """
    yield from get_files(config.export_path)
    # get the live file from ~/.mozilla/.... (see ffexport.save_hist)
    tmp_dir: str = tempfile.mkdtemp()
    # I only use the one profile, so profile defaults to *
    backup_history(browser="firefox", to=Path(tmp_dir))
    live_copy: Sequence[Path] = get_files(tmp_dir, glob="*.sqlite")
    assert len(live_copy) == 1, f"Couldn't find live history backup in {tmp_dir}"
    yield live_copy[0]


Results = Iterator[Visit]

def history(from_paths=inputs) -> Results:
    """
    used like:
    import my.browsing
    visits = list(my.browsing.history())
    """
    yield from read_and_merge(*from_paths())

