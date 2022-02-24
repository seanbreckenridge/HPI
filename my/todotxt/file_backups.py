"""
Parses todotxt (http://todotxt.org/) done.txt and todo.txt files
"""

REQUIRES = ["pytodotxt>=1.4.0"]


# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import todotxt as user_config  # type: ignore[attr-defined]
from my.core import PathIsh, Paths, dataclass


# TODO: do something with the todo.txt files?
# currently just backing them up so possibly could figure out
# which day a todo was created, or to do statistics on # of todos over
# time
# currently only the done.txt are being merged and the live_file
# is parsed to get current todos


from pathlib import Path
from datetime import datetime
from typing import (
    NamedTuple,
    cast,
    Iterator,
    Set,
    Any,
    List,
    Tuple,
    Dict,
    Callable,
    Iterable,
    Optional,
)
from itertools import chain

from more_itertools import unique_everseen
from pytodotxt import TodoTxtParser, Task  # type: ignore[import]

from my.core import get_files, Stats, LazyLogger


@dataclass
class config(user_config.file_backups):
    # path[s]/glob to the exported zsh history files
    # expects files like:
    # 20200827T192309Z-done.txt
    # 20200827T192309Z-todo.txt
    # 20200829T192309Z-done.txt
    # 20200829T192309Z-todo.txt
    export_path: Paths

    # the currently being used todo.txt file, at ~/.todo/todo.txt or ~/.config/todo.txt
    live_file: Optional[PathIsh]


logger = LazyLogger(__name__)


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

    # custom hash for detecting changes in events
    def __hash__(self) -> int:
        return hash(self.description)


def inputs() -> Iterable[Tuple[datetime, Path]]:
    """Returns all todo/done.txt files"""
    dones = get_files(config.export_path)
    res: List[Tuple[datetime, Path]] = []
    for todone in dones:
        dt = datetime.strptime(todone.stem.split("-")[0], "%Y%m%dT%H%M%SZ")
        res.append((dt, todone))
    return res


Results = Iterator[Todo]


def completed(
    from_paths: Callable[[], Iterable[Tuple[datetime, Path]]] = inputs
) -> Results:
    """
    Merges all todo.txt/done.txt files and filters to return the history of todos I've completed
    """
    yield from filter(
        lambda t: t.is_completed,
        unique_everseen(
            chain(*map(_parse_file, [p for (_, p) in from_paths()])),
            key=lambda t: (t.completion_date, t.description),
        ),
    )


def todos(from_file: Optional[PathIsh] = config.live_file) -> Results:
    """
    Parses the currently in use todo.txt file (returns my current todos)

    Note: if you don't have a todo.txt file on your system,
    this just returns an empty list
    """
    if from_file is None:
        return
    p = Path(from_file).expanduser().absolute()
    if p.exists():
        yield from _parse_file(p)
    else:
        logger.warning(f"'{p}' does not exist")


class TodoEvent(NamedTuple):
    todo: Todo
    dt: datetime
    # type/false for added/completed
    added: bool


TodoState = Tuple[datetime, List[Todo]]


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
        tset: Set[Todo] = set()
        # for each todo
        for td in tlist:
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
    for t in TodoTxtParser(task_type=Todo).parse_file(todofile):
        yield cast(Todo, t)


def stats() -> Stats:
    from my.core import stat

    return {
        **stat(todos),
        **stat(completed),
        **stat(events),
    }
