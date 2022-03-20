"""
Parses when I added/removed newsboat subscriptions
"""

REQUIRES = ["git+https://github.com/seanbreckenridge/git_doc_history"]


# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import rss as user_config  # type: ignore[attr-defined]


from pathlib import Path
from datetime import datetime
from typing import (
    Iterator,
    List,
)

from git_doc_history import (
    DocHistory,
    parse_snapshot_diffs,
    Diff,
)

from my.core import Stats, PathIsh, dataclass


@dataclass
class config(user_config.newsboat.git_history):
    # path to the git backup directory
    export_path: PathIsh


RSS_FILES = ["urls"]


def input() -> DocHistory:
    return DocHistory(
        backup_dir=Path(config.export_path).expanduser().absolute(),
        copy_files=RSS_FILES,
    )


Results = Iterator[str]


def _parse_buffer(buf: bytes) -> List[str]:
    return buf.decode("utf-8").strip().splitlines()


def subscriptions() -> Results:
    yield from _parse_buffer(input().extract_buffer_at(RSS_FILES[0], at=datetime.now()))


def events() -> Iterator[Diff]:
    yield from parse_snapshot_diffs(
        input(),
        file="urls",
    )


def stats() -> Stats:
    from my.core import stat

    return {
        **stat(subscriptions),
        **stat(events),
    }
