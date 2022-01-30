"""
Parse Message Dates from Skypes GDPR JSON export
"""

REQUIRES = ["dateparser"]

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
from typing import Iterator, Sequence
from itertools import chain

import dateparser

from my.core import get_files, LazyLogger
from my.utils.input_source import InputSource

logger = LazyLogger(__name__, level="warning")


Results = Iterator[datetime]


def inputs() -> Sequence[Path]:
    return get_files(config.export_path)


@mcachew(
    depends_on=lambda: [str(p) for p in sorted(inputs())],
    logger=logger,
)
def timestamps(from_paths: InputSource = inputs) -> Results:
    yield from chain(*map(_parse_file, from_paths()))


def _parse_file(post_file: Path) -> Results:
    items = json.loads(post_file.read_text())
    for conv in items["conversations"]:
        for msg in conv["MessageList"]:
            d = dateparser.parse(msg["originalarrivaltime"].rstrip("Z"))
            if d is not None:
                yield d


def stats() -> Stats:
    from my.core import stat

    return {**stat(timestamps)}
