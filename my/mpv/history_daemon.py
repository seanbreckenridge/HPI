"""
Any Media being played on my computer with mpv
Uses my mpv-history-daemon
https://github.com/seanbreckenridge/mpv-history-daemon
"""

REQUIRES = ["git+https://github.com/seanbreckenridge/mpv-history-daemon"]

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import mpv as user_config  # type: ignore[attr-defined]

from typing import Iterator, Sequence, Optional
from my.core import Paths, dataclass, make_config


@dataclass
class mpv_config(user_config.history_daemon):
    # glob to the JSON files that the daemon writes whenever Im using mpv
    export_path: Paths

    # amount of song I should have listened to to qualify it as a listen (e.g. 0.5, 0.75)
    require_percent: Optional[float] = None


config = make_config(mpv_config)


import os
from pathlib import Path

from mpv_history_daemon.events import (
    Media,
    all_history as M_all_history,
    _actually_listened_to,
)

from my.core import get_files, Stats, LazyLogger
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
    perc = config.require_percent or 0.75
    # fallback to library func
    return _actually_listened_to(m, require_listened_to_percent=perc)


def all_history(from_paths: InputSource = inputs) -> Results:
    yield from M_all_history(list(from_paths()))


def history(from_paths: InputSource = inputs) -> Results:
    yield from filter(_filter_by, all_history(from_paths))
