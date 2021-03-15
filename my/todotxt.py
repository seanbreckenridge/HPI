"""
Parses todotxt (http://todotxt.org/) done.txt and todo.txt files
"""

from typing import Optional

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import todotxt as user_config  # type: ignore[attr-defined]
from my.core import PathIsh, Paths, dataclass


# TODO: do something with the todo.txt files?
# currently just backing them up so possibly could figure out
# which day a todo was created, or to do statistics on # of todos over
# time
# currently only the done.txt are being merged and the live_file
# is parsed to get current todos


@dataclass
class config(user_config):
    # path[s]/glob to the exported zsh history files
    # expects files like:
    # 20200827T192309Z-done.txt
    # 20200827T192309Z-todo.txt
    # 20200829T192309Z-done.txt
    # 20200829T192309Z-todo.txt
    export_path: Paths

    # the currently being used todo.txt file, at ~/.todo/todo.txt or ~/.config/todo.txt
    live_file: Optional[PathIsh]


import warnings
from pathlib import Path
from datetime import datetime
from typing import NamedTuple, Iterator, Set, List, Tuple, Sequence, Dict
from itertools import chain


from my.core import get_files, warn_if_empty, Stats, LazyLogger, Res
from my.core.common import listify

# pip3 install topydo
from topydo.lib.TodoParser import parse_line  # type: ignore[import]

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

    def __hash__(self):
        return hash(self.text)


@listify
def inputs() -> Sequence[Tuple[datetime, Path]]:  # type: ignore[misc]
    """Returns all todo/done.txt files"""
    dones = get_files(config.export_path)
    for todone in dones:
        dt = datetime.strptime(todone.stem.split("-")[0], "%Y%m%dT%H%M%SZ")
        yield (dt, todone)


Results = Iterator[Res[Todo]]


def completed(from_paths=inputs) -> Results:
    """
    Merges all todo.txt/done.txt files and filters to return the history of todos I've completed
    """
    for td in _merge_histories(*map(_parse_file, map(lambda r: r[1], from_paths()))):
        if isinstance(td, Exception):
            yield td
        else:
            if td.completed:
                yield td


def todos(from_file: Optional[PathIsh] = config.live_file) -> Results:
    """
    Parses the currently in use todo.txt file (returns my current todos)
    """
    if from_file is None:
        warnings.warn(f"Did not receive a valid 'live_file' to read from: {from_file}")
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


class TodoEvent(NamedTuple):
    todo: Todo
    dt: datetime
    # type/false for added/completed
    added: bool


TodoState = Tuple[datetime, List[Res[Todo]]]


def events() -> Iterator[TodoEvent]:
    """
    Keeps track when I added/completed todos
    """
    current_state: Dict[Todo, datetime] = {}
    todo_snapshots: List[TodoState] = []
    for dt, tpath in inputs():
        # ignore -done.txt files
        if tpath.stem.endswith("-todo"):
            todo_snapshots.append((dt, list(_parse_file(tpath))))
    todo_snapshots.sort(key=lambda tsnap: tsnap[0])

    for dt, tlist in todo_snapshots:
        # ignore exceptions while computing events
        if isinstance(tlist, Exception):
            continue
        tset: Set[Todo] = set()
        # for each todo
        for td in tlist:
            if isinstance(td, Exception):
                # ignore exceptions while computing events
                continue
            tset.add(td)
            if td in current_state:
                continue
            current_state[td] = dt
            yield TodoEvent(todo=td, dt=dt, added=True)

        # check if any were removed
        for td in list(current_state):
            if td not in tset:
                yield TodoEvent(todo=td, dt=dt, added=False)
                del current_state[td]


def _parse_file(todofile: Path) -> Results:
    for line in todofile.open():
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


def stats() -> Stats:
    from my.core import stat

    return {
        **stat(todos),
        **stat(completed),
        **stat(events),
    }
