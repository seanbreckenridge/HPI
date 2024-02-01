"""
Parses history from https://github.com/seanbreckenridge/aw-watcher-window
using https://github.com/seanbreckenridge/active_window
"""

REQUIRES = [
    "git+https://github.com/seanbreckenridge/aw-watcher-window",
    "git+https://github.com/seanbreckenridge/active_window",
]

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import activitywatch as user_config  # type: ignore[attr-defined]

from pathlib import Path
from typing import Iterator, Sequence, Union
from functools import partial
from itertools import chain

from my.core import get_files, Stats, Paths, dataclass, make_logger, make_config
from my.utils.input_source import InputSource

from more_itertools import unique_everseen

import active_window.parse as AW

logger = make_logger(__name__)


@dataclass
class window_config(user_config.active_window):
    # path[s]/glob to the backed up aw-window JSON/window_watcher CSV history files
    export_path: Paths
    error_policy: AW.ErrorPolicy = "drop"


config = make_config(window_config)


Result = Union[AW.AWAndroidEvent, AW.AWComputerEvent, AW.AWWindowWatcherEvent]
Results = Iterator[Result]


def inputs() -> Sequence[Path]:
    return get_files(config.export_path)


def history(from_paths: InputSource = inputs) -> Results:
    yield from unique_everseen(
        chain(
            *map(
                partial(
                    AW.parse_window_events,
                    logger=logger,
                    error_policy=config.error_policy,
                ),
                from_paths(),
            )
        ),
        key=lambda e: e.timestamp,
    )


def stats() -> Stats:
    from my.core import stat

    return {**stat(history)}
