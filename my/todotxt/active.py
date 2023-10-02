"""
Parses your active todotxt (http://todotxt.org/) done.txt and todo.txt
"""

REQUIRES = ["pytodotxt>=1.5.0"]


# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import todotxt as user_config  # type: ignore[attr-defined]


from pathlib import Path
from typing import (
    Tuple,
    Iterator,
)

from my.core import Stats, PathIsh, dataclass
from .common import Todo, TODOTXT_FILES, parse_todotxt_buffer


@dataclass
class config(user_config.active):
    # path to your active todo.txt directory
    # this is the same place todo.sh stores your files
    export_path: PathIsh


def inputs() -> Tuple[Path, Path]:
    p = Path(config.export_path).expanduser().absolute()
    if not p.exists():
        raise FileNotFoundError(f"todotxt export path {p} doesn't exist")
    # todo.txt, done.txt
    return (
        p / TODOTXT_FILES[0],
        p / TODOTXT_FILES[1],
    )


Results = Iterator[Todo]


def done() -> Results:
    df = inputs()[1]
    if not Path(df).exists():
        return
    yield from parse_todotxt_buffer(Path(df).read_text())


def todos() -> Results:
    tf = inputs()[0]
    if not tf.exists():
        return
    yield from parse_todotxt_buffer(tf.read_text())


def stats() -> Stats:
    from my.core import stat

    return {
        **stat(todos),
        **stat(done),
    }
