"""
Parses generic event data from my parsed GDPR data
from: https://github.com/seanbreckenridge/blizzard_gdpr_parser
"""

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import blizzard as user_config  # type: ignore[attr-defined]
from my.core import Paths, dataclass, LazyLogger
from my.core.common import mcachew


@dataclass
class config(user_config):
    # path to the exported data
    export_path: Paths


import json
from pathlib import Path
from datetime import datetime
from typing import NamedTuple, Iterator, Sequence, List
from itertools import chain

from my.core import get_files, Stats
from .utils.time import parse_datetime_sec
from .utils.common import InputSource


logger = LazyLogger(__name__, level="warning")


def inputs() -> Sequence[Path]:
    return get_files(config.export_path)


def _cachew_depends_on(for_paths: InputSource = inputs) -> List[float]:
    return [p.stat().st_mtime for p in for_paths()]


class Event(NamedTuple):
    dt: datetime
    event_tag: str
    metadata: List[str]


Results = Iterator[Event]


@mcachew(depends_on=_cachew_depends_on, logger=logger)
def events(from_paths: InputSource = inputs) -> Results:
    yield from chain(*map(_parse_json_file, from_paths()))


def _parse_json_file(p: Path) -> Results:
    for e_info in json.loads(p.read_text()):
        dt, meta_tuple = e_info
        meta_tag, meta_joined = meta_tuple
        yield Event(
            dt=parse_datetime_sec(dt),
            event_tag=meta_tag,
            metadata=meta_joined.split("|"),
        )


def stats() -> Stats:
    from my.core import stat

    return {**stat(events)}
