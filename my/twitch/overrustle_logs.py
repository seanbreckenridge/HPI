"""
Reads parsed information from the overrustle logs dump
https://github.com/seanbreckenridge/overrustle_parser
"""

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import twitch as user_config  # type: ignore[attr-defined]

from my.core import Paths, dataclass


@dataclass
class config(user_config.overrustle):
    export_path: Paths  # parsed overrustle_parser json files


import json
from pathlib import Path
from typing import Sequence, List

from my.core import make_logger
from my.core.common import get_files, mcachew, Stats
from my.utils.time import parse_datetime_sec
from my.utils.input_source import InputSource

from .common import Event, Results

logger = make_logger(__name__)


def inputs() -> Sequence[Path]:
    return get_files(config.export_path)


def _cachew_depends_on(for_paths: InputSource = inputs) -> List[float]:
    return [p.stat().st_mtime for p in for_paths()]


@mcachew(depends_on=_cachew_depends_on, logger=logger)
def events(from_paths: InputSource = inputs) -> Results:
    for file in from_paths():
        yield from _parse_json_dump(file)


def _parse_json_dump(p: Path) -> Results:
    for blob in json.loads(p.read_text()):
        yield Event(
            event_type="chatlog",
            dt=parse_datetime_sec(blob["dt"]),
            channel=blob["channel"],
            context=blob["message"],
        )


def stats() -> Stats:
    from my.core import stat

    return {**stat(events)}
