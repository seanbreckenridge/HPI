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


from pathlib import Path
from typing import Sequence
from datetime import datetime
from typing import NamedTuple, Iterator

from autotui.shortcuts import load_from

from my.core import get_files, Stats, LazyLogger
from .utils.common import InputSource


def inputs() -> Sequence[Path]:
    return get_files(config.export_path)


logger = LazyLogger(__name__)

# represents one post on a forum entry
class Post(NamedTuple):
    date: datetime
    post_title: str
    post_url: str
    contents: str
    forum_name: str


Results = Iterator[Post]


def history(from_paths: InputSource = inputs) -> Results:
    for path in from_paths():
        # TODO: fix types in autotui to bind to first arg?
        yield from load_from(Post, path)  # type: ignore[misc]


def stats() -> Stats:
    from my.core import stat

    return {**stat(history)}
