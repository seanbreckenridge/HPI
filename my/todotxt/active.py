"""
Parses your active todotxt (http://todotxt.org/) done.txt and todo.txt
"""

REQUIRES = [
    "pytodotxt>=1.5.0",
]


# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import todotxt as user_config  # type: ignore[attr-defined]


from pathlib import Path
from typing import (
    cast,
    Union,
    Iterator,
    List,
)

from pytodotxt import TodoTxtParser  # type: ignore[import]

from my.core import Stats, PathIsh, dataclass
from .common import Todo


@dataclass
class config(user_config.active):
    # path to the git backup directory
    export_path: PathIsh


@dataclass
class Inputs:
    export_path: Path
    todo_file: Path
    done_file: Path

    @classmethod
    def from_pathish(cls, p: PathIsh) -> "Inputs":
        p = Path(p).expanduser().absolute()
        return cls(
            export_path=p,
            todo_file=p / "todo.txt",
            done_file=p / "done.txt",
        )


def inputs() -> Inputs:
    return Inputs.from_pathish(config.export_path)


def _parse_todotxt_buffer(data: Union[str, bytes]) -> List[Todo]:
    return cast(List[Todo], TodoTxtParser(task_type=Todo).parse(data))


Results = Iterator[Todo]


def done() -> Results:
    df = inputs().done_file
    if not df.exists():
        return
    yield from _parse_todotxt_buffer(df.read_text())


def todos() -> Results:
    tf = inputs().todo_file
    if not tf.exists():
        return
    yield from _parse_todotxt_buffer(tf.read_text())


def stats() -> Stats:
    from my.core import stat

    return {
        **stat(todos),
        **stat(done),
    }
