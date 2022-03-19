"""
Parses piazza posts scraped by
https://github.com/seanbreckenridge/piazza-scraper
"""

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import piazza as user_config  # type: ignore[attr-defined]
from my.core import Paths, dataclass


@dataclass
class config(user_config.scraper):
    # path to the exported data
    export_path: Paths


import os
from pathlib import Path
from typing import Iterator, Sequence, Optional

from my.core import get_files, Stats

from piazza_scraper.parse import Post, Export


def inputs() -> Sequence[Path]:
    return get_files(config.export_path)


def classes() -> Iterator[Export]:
    for file in inputs():
        yield Export.parse_file(file)


def _all_posts() -> Iterator[Post]:
    for exp in classes():
        for post in exp.posts:
            yield from post.walk_posts()


def posts() -> Iterator[Post]:
    """
    Infer my user id by checking the stats/users area
    Parse all posts, and return ones made by me
    """
    for exp in classes():
        # hmm -- it seems that I'm always the only user in this?
        # will check an envvar incase someone else has issues configuring this/has different results
        # feel free to open an issue
        user_id: Optional[str] = os.environ.get("PIAZZA_UID")
        if user_id is None:
            assert (
                len(exp.users) > 0
            ), "Could not infer user id, set the PIAZZA_UID environment variable to your users' uid"
            user_id = exp.users[0].uid

        assert user_id is not None
        for post in exp.posts:
            yield from post.walk_posts_by_me(user_id)


def stats() -> Stats:
    from my.core import stat

    return {
        **stat(posts),
    }
