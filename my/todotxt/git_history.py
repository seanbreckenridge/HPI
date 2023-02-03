"""
Parses todotxt (http://todotxt.org/) done.txt and todo.txt files
"""

REQUIRES = [
    "pytodotxt>=1.4.0",
    "git+https://github.com/seanbreckenridge/git_doc_history",
]


# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import todotxt as user_config  # type: ignore[attr-defined]


from pathlib import Path
from datetime import datetime, timezone
from typing import (
    cast,
    Any,
    Union,
    Iterator,
    List,
    Dict,
)

from git_doc_history import DocHistory, DocHistorySnapshot, parse_snapshot_diffs, Action
from pytodotxt import TodoTxtParser, Task  # type: ignore[import]

from my.core import Stats, PathIsh, dataclass


@dataclass
class config(user_config.git_history):
    # path to the git backup directory
    export_path: PathIsh


class Todo(Task):
    # support serializing with hpi query
    def _serialize(self) -> Dict[str, Any]:
        assert self._raw is not None
        return {
            "completed": self.is_completed,
            "completion_date": self.completion_date,
            "creation_date": self.creation_date,
            "priority": self.priority,
            "text": self.bare_description(),
            "projects": self.projects,
            "contexts": self.contexts,
            "attributes": self.attributes,
            "raw": self._raw,
        }

    @property
    def bare(self) -> str:
        if hasattr(self, "_bare"):
            return str(self._bare)
        setattr(self, "_bare", self.bare_description())
        return cast(str, self._bare)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Task):
            return False
        return cast(bool, self.bare == other.bare)

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.bare)


TODOTXT_FILES = ["todo.txt", "done.txt"]


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
