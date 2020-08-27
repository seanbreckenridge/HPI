"""
Parses todotxt (http://todotxt.org/) done.txt and todo.txt files
"""

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import todotxt as user_config  # type: ignore

from dataclasses import dataclass
from typing import Optional

from .core import PathIsh, Paths


# TODO: do something with the todo.txt files?
# currently just backing them up so possibly could figure out
# which day a todo was created, or to do statistics on # of todos over
# time
# currently only the done.txt are being merged and the live_file
# is parsed to get current todos


@dataclass
class todotxt(user_config):
    # path[s]/glob to the exported zsh history files
    # expects files like:
    # 20200827T192309Z-done.txt
    # 20200827T192309Z-todo.txt
    # 20200829T192309Z-done.txt
    # 20200829T192309Z-todo.txt
    export_path: Paths

    # the currently being used todo.txt file, at ~/.todo/todo.txt or ~/.config/todo.txt
    live_file: Optional[PathIsh]


from .core.cfg import make_config

config = make_config(todotxt)

#######

import warnings
from pathlib import Path
from typing import Sequence

from .core import get_files, warn_if_empty
from .core.common import listify


@listify
def inputs() -> Sequence[Path]:
    """
    Returns all todo.txt related files
    """
    yield from get_files(config.export_path, glob="*.txt")


from datetime import datetime
from typing import NamedTuple, Iterator, Set, List, Tuple
from itertools import chain

from .core.error import Res
from .core.common import LazyLogger
from .core.file import yield_lines

# pip3 install topydo
from topydo.lib.TodoParser import parse_line

logger = LazyLogger(__name__)


class Todo(NamedTuple):
    completed: bool
    completion_date: Optional[datetime]
    creation_date: Optional[datetime]
    priority: Optional[str]
    text: str
    projects: List[str]
    contexts: List[str]
    tags: List[str]


Results = Iterator[Res[Todo]]


def history(from_paths=inputs) -> Results:
    """
    Merges the done.txt files to return the history of todos I've completed
    """
    yield from _merge_histories(*map(_parse_file, from_paths()))


def todos(from_file: Optional[PathIsh] = config.live_file) -> Results:
    """
    Parses the currently in use todo.txt file
    """
    if from_file is None:
        warnings.warn(f"Did not recieve a valid 'live_file' to read from: {from_file}")
    else:
        p = Path(from_file).expanduser().absolute()
        if p.exists():
            yield from _parse_file(p)
        else:
            warnings.warn(f"{p} does not exist")


@warn_if_empty
def _merge_histories(*sources: Results) -> Results:
    emitted: Set[Tuple[Optional[datetime], str]] = set()
    for e in chain(*sources):
        if isinstance(e, Exception):
            yield e
            continue
        key = (e.completion_date, e.text)
        if key in emitted:
            # logger.debug('ignoring %s: %s', key, e)
            continue
        yield e
        emitted.add(key)


def _parse_file(todofile: Path):
    for line in yield_lines(todofile):
        try:
            t = parse_line(line)
            yield Todo(
                completed=t["completed"],
                completion_date=t["completionDate"],
                creation_date=t["creationDate"],
                priority=t["priority"],
                text=t["text"],
                projects=t["projects"],
                contexts=t["contexts"],
                tags=t["tags"],
            )
        except Exception as e:
            yield e
