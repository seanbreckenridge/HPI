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
from typing import Iterator, Sequence, List

from mpv_history_daemon.events import (
    Media,
    all_history as M_all_history,
    _actually_listened_to,
)

from my.core import get_files, Stats, LazyLogger
from my.core.common import mcachew

# monkey patch logs
if "HPI_LOGS" in os.environ:
    from logzero import setup_logger  # type: ignore[import]
    from my.core.logging import mklevel
    import mpv_history_daemon.events

    mpv_history_daemon.events.logger = setup_logger(
        name="mpv_history_events", level=mklevel(os.environ["HPI_LOGS"])
    )


logger = LazyLogger(__name__, level="warning")

Results = Iterator[Media]


def stats() -> Stats:
    from my.core import stat

    return {
        **stat(history),
    }


def inputs() -> Sequence[Path]:
    return get_files(config.export_path)


def _cachew_depends_on() -> List[float]:
    return [p.stat().st_mtime for p in sorted(inputs())]


@mcachew(depends_on=_cachew_depends_on, logger=logger)
def all_history() -> Results:
    yield from M_all_history(inputs())


# filter out items I probably didn't listen to
@mcachew(depends_on=_cachew_depends_on, logger=logger)
def history() -> Results:
    yield from filter(_actually_listened_to, all_history())
