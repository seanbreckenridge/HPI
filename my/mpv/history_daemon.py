"""
Any Media being played on my computer with mpv
Uses my mpv-history-daemon
https://github.com/seanbreckenridge/mpv-history-daemon
"""

REQUIRES = ["git+https://github.com/seanbreckenridge/mpv-history-daemon"]

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
from my.utils.input_source import InputSource

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


def _cachew_depends_on(for_paths: InputSource = inputs) -> List[float]:
    return [p.stat().st_mtime for p in sorted(for_paths())]


def _filter_by(m: Media) -> bool:
    if m.is_stream:
        return True
    # if duration is under 10 minutes, but listen_time is over
    # 3 hours, probably a broken item, caused by hanging mpv/socket?
    # I only have 2 of these, in the 13,000 or so history items
    if m.media_duration is not None and m.media_duration < 600:
        if m.listen_time > 10800:
            logger.debug(f"Assuming this is a broken file: {str(m)}")
            return False
    # fallback to library func
    return _actually_listened_to(m)


@mcachew(depends_on=_cachew_depends_on, logger=logger)
def all_history(from_paths: InputSource = inputs) -> Results:
    yield from M_all_history(list(from_paths()))


# filter out items I probably didn't listen to
@mcachew(depends_on=_cachew_depends_on, logger=logger)
def history(from_paths: InputSource = inputs) -> Results:
    yield from filter(_filter_by, all_history(from_paths))
