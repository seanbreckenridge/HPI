"""
Parse Message Dates from Skypes GDPR JSON export
"""

# Isn't a lot of data here, seems a lot of the old
# data is gone. Only parses a couple messages, might
# as well use the datetimes for context on when I
# was using skype

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import skype as user_config

from dataclasses import dataclass

from .core import Paths, Stats
from .core.common import mcachew
from .core.cachew import cache_dir


@dataclass
class skype(user_config):
    # path[s]/glob to the skype JSON files
    export_path: Paths


from .core.cfg import make_config

config = make_config(skype)

#######

import json
from pathlib import Path
from typing import Sequence

from .core import get_files


def inputs() -> Sequence[Path]:
    return get_files(config.export_path)


from datetime import datetime
from typing import Iterator, Optional
from itertools import chain

import dateparser

from .core.common import LazyLogger

logger = LazyLogger(__name__, level="warning")


Results = Iterator[datetime]
OptResults = Iterator[Optional[datetime]]


@mcachew(
    cache_path=cache_dir(),
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
    from .core import stat

    return {**stat(timestamps)}
