"""
Parse Message Dates from Skypes GDPR JSON export
"""

# Isn't a lot of data here, seems a lot of the old
# data is gone. Only parses a couple messages, might
# as well use the datetimes for context on when I
# was using skype

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import skype as user_config  # type: ignore[attr-defined]

from my.core import Paths, Stats, dataclass
from my.core.common import mcachew


@dataclass
class config(user_config):
    # path[s]/glob to the skype JSON files
    export_path: Paths


import json
from pathlib import Path
from datetime import datetime
from typing import Iterator, Optional, Sequence
from itertools import chain

import dateparser

from my.core import get_files, LazyLogger

logger = LazyLogger(__name__, level="warning")


Results = Iterator[datetime]
OptResults = Iterator[Optional[datetime]]


def inputs() -> Sequence[Path]:
    return get_files(config.export_path)


@mcachew(
    depends_on=lambda: list(map(str, inputs())),
    logger=logger,
)
def timestamps(from_paths=inputs) -> Results:
    for d in chain(*map(_parse_file, from_paths())):
        if d is not None:
            yield d


def _parse_file(post_file: Path) -> OptResults:
    items = json.loads(post_file.read_text())
    for conv in items["conversations"]:
        for msg in conv["MessageList"]:
            yield dateparser.parse(msg["originalarrivaltime"].rstrip("Z"))


def stats() -> Stats:
    from my.core import stat

    return {**stat(timestamps)}
