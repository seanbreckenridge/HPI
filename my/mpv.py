"""
Any Media being played on my computer with mpv
Uses my mpv-history-daemon
https://github.com/seanbreckenridge/mpv-history-daemon
"""

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import mpv as user_config  # type: ignore[attr-defined]

from my.core import Paths, dataclass


@dataclass
class config(user_config):
    # glob to the JSON files that the daemon writes whenever Im using mpv
    export_path: Paths


import os
from pathlib import Path
from typing import Iterator, Sequence

import mpv_history_daemon.events
from mpv_history_daemon.events import Media

from my.core import get_files, Stats

# monkey patch logs
if "HPI_LOGS" in os.environ:
    from logzero import setup_logger  # type: ignore[import]
    from my.core.logging import mklevel

    mpv_history_daemon.events.logger = setup_logger(
        name="mpv_history_events", level=mklevel(os.environ["HPI_LOGS"])
    )

Results = Iterator[Media]


def stats() -> Stats:
    from my.core import stat

    return {
        **stat(history),
    }


def inputs() -> Sequence[Path]:
    return get_files(config.export_path)


def all_history(from_paths=inputs) -> Results:
    yield from mpv_history_daemon.events.all_history(from_paths())


# filter out items I probably didn't listen to
def history(from_paths=inputs) -> Results:
    yield from mpv_history_daemon.events.history(from_paths())
