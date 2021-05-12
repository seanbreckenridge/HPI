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

from my.core import get_files
from my.utils.time import parse_datetime_sec

from .common import Event, Results


def events(from_paths: Paths = config.export_path) -> Results:
    for file in get_files(from_paths):
        yield from _parse_json_dump(file)


def _parse_json_dump(p: Path) -> Results:
    for blob in json.loads(p.read_text()):
        yield Event(
            event_type="chatlog",
            dt=parse_datetime_sec(blob["dt"]),
            channel=blob["channel"],
            context=blob["message"],
        )
