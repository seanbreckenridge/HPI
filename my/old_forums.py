"""
Manually Scraped Forum Posts from Random Forums I've used in the past
https://github.com/seanbreckenridge/forum_parser
"""

REQUIRES = ["git+https://github.com/seanbreckenridge/old_forums"]

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import old_forums as user_config  # type: ignore[attr-defined]

from my.core import Paths, dataclass


@dataclass
class config(user_config):
    # path[s]/glob to the folder which contains JSON/HTML files
    export_path: Paths


import os
from pathlib import Path
from typing import Sequence, Iterator

from autotui.shortcuts import load_from
from old_forums.forum import Post  # model from lib
from old_forums.achievements import AchievementSelector, Achievement

from my.core import get_files, Stats
from .utils.common import InputSource


def forum_post_files() -> Sequence[Path]:
    return get_files(config.export_path, glob="*.json")


def achievement_files() -> Sequence[Path]:
    return get_files(config.export_path, glob="*.html")


def forum_posts(from_paths: InputSource = forum_post_files) -> Iterator[Post]:
    for path in from_paths():
        yield from load_from(Post, path)


def achievements(from_paths: InputSource = achievement_files) -> Iterator[Achievement]:
    # quite personal, lets me specify CSS selectors as a JSON config file, see:
    # https://github.com/seanbreckenridge/old_forums
    sels = AchievementSelector.load_from_blob(open(os.environ["OLD_FORUMS_SELECTORS"]))
    for path in from_paths():
        with path.open("r") as f:
            yield from Achievement.parse_using_selectors(f, sels)


def stats() -> Stats:
    from my.core import stat

    return {**stat(forum_posts), **stat(achievements)}
