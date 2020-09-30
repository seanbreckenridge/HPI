"""
Parses generic event data from my parsed GDPR data
from: https://github.com/seanbreckenridge/blizzard_gdpr_parser
"""

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import blizzard as user_config  # type: ignore

from dataclasses import dataclass

from ..core import Paths


@dataclass
class blizzard(user_config):
    # path to the exported data
    export_path: Paths


from ..core.cfg import make_config

config = make_config(blizzard)

#######

import json
from pathlib import Path
from datetime import datetime
from typing import NamedTuple, Iterator, Sequence, List
from itertools import chain

from ..core import get_files
from ..core.time import parse_datetime_sec


def inputs() -> Sequence[Path]:
    return get_files(config.export_path)


class Event(NamedTuple):
    dt: datetime
    event_tag: str
    metadata: List[str]


Results = Iterator[Event]


def events(from_paths=inputs) -> Results:
    yield from chain(*map(_parse_json_file, from_paths()))


def _parse_json_file(p: Path) -> Results:
    items = json.loads(p.read_text())
    for e_info in items:
        dt, meta_tuple = e_info
        meta_tag, meta_joined = meta_tuple
        yield Event(
            dt=parse_datetime_sec(dt),
            event_tag=meta_tag,
            metadata=meta_joined.split("|"),
        )


def stats():
    from ..core import stat

    return {**stat(events)}
