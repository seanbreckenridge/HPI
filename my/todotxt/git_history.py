"""
Parses todotxt (http://todotxt.org/) done.txt and todo.txt history
from https://github.com/seanbreckenridge/git_doc_history backups
"""

REQUIRES = [
    "pytodotxt>=1.5.0",
    "git+https://github.com/seanbreckenridge/git_doc_history",
]


# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import todotxt as user_config  # type: ignore[attr-defined]


from pathlib import Path
from datetime import datetime, timezone
from typing import (
    cast,
    Union,
    Iterator,
    List,
)

from git_doc_history import DocHistory, DocHistorySnapshot, parse_snapshot_diffs, Action
from pytodotxt import TodoTxtParser  # type: ignore[import]

from my.core import Stats, PathIsh, dataclass
from .common import Todo, TODOTXT_FILES


@dataclass
class config(user_config.git_history):
    # path to the git backup directory
    export_path: PathIsh


def input() -> DocHistory:
    return DocHistory(
        backup_dir=Path(config.export_path).expanduser().absolute(),
        copy_files=TODOTXT_FILES,
    )


def _parse_todotxt_buffer(data: Union[str, bytes]) -> List[Todo]:
    return cast(List[Todo], TodoTxtParser(task_type=Todo).parse(data))


def _parse_into_todos(doc: DocHistorySnapshot) -> List[Todo]:
    return _parse_todotxt_buffer(doc.data)


Results = Iterator[Todo]


# These work by grabbing the latest version of the file
# from the git repo, so they may not always be up to date
# if you don't update git_doc_history often enough
def done() -> Results:
    yield from _parse_todotxt_buffer(
        input().extract_buffer_at("done.txt", at=datetime.now())
    )


def todos() -> Results:
    yield from _parse_todotxt_buffer(
        input().extract_buffer_at("todo.txt", at=datetime.now())
    )


@dataclass
class TodoEvent:
    todo: Todo
    dt: datetime
    action: Action


def events() -> Iterator[TodoEvent]:
    """
    Keeps track when I added/completed todos
    """
    for diff in parse_snapshot_diffs(
        input(),
        file="todo.txt",
        parse_func=_parse_into_todos,
    ):
        yield TodoEvent(
            todo=diff.data,
            dt=datetime.fromtimestamp(diff.epoch_time, tz=timezone.utc),
            action=diff.action,
        )


def stats() -> Stats:
    from my.core import stat

    return {
        **stat(todos),
        **stat(done),
        **stat(events),
    }
