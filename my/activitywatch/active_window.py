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
from itertools import chain

from my.core import get_files, Stats, Paths, dataclass
from my.utils.input_source import InputSource

from more_itertools import unique_everseen

import active_window.parse as AW


@dataclass
class config(user_config.active_window):
    # path[s]/glob to the backed up aw-window JSON/window_watcher CSV history files
    export_path: Paths


Result = Union[AW.AWAndroidEvent, AW.AWComputerEvent, AW.AWWindowWatcherEvent]
Results = Iterator[Result]


def inputs() -> Sequence[Path]:
    return get_files(config.export_path)


def history(from_paths: InputSource = inputs) -> Results:
    yield from unique_everseen(
        chain(*map(AW.parse_window_events, from_paths())), key=lambda e: e.timestamp
    )


def stats() -> Stats:
    from my.core import stat

    return {**stat(history)}
