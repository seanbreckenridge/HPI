"""
Manually Scraped Forum Posts from Random Forums I've used in the past
https://github.com/seanbreckenridge/forum_parser
"""

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import old_forums as user_config  # type: ignore[attr-defined]

from my.core import Paths, dataclass


@dataclass
class config(user_config):
    # path[s]/glob to the parsed JSON files
    export_path: Paths


import json
from pathlib import Path
from typing import Sequence
from datetime import datetime
from typing import NamedTuple, Iterator
from itertools import chain

from my.core import get_files, Stats, LazyLogger
from .utils.time import parse_datetime_sec


def inputs() -> Sequence[Path]:
    return get_files(config.export_path)


logger = LazyLogger(__name__)

# represents one post on a forum entry
class Post(NamedTuple):
    dt: datetime
    post_title: str
    post_url: str
    post_contents: str  # eh, doesnt match contents, whatever
    forum_name: str


Results = Iterator[Post]


def history(from_paths=inputs) -> Results:
    yield from chain(*map(_parse_file, from_paths()))


def _parse_file(post_file: Path) -> Results:
    for p in json.loads(post_file.read_text()):
        yield Post(
            dt=parse_datetime_sec(p["date"]),
            post_title=p["post_title"],
            post_url=p["post_url"],
            post_contents=p["contents"],
            forum_name=p["forum_name"],
        )


def stats() -> Stats:
    from my.core import stat

    return {**stat(history)}
