from pathlib import Path
from typing import Callable, Iterable

from my.core import __NOT_HPI_MODULE__  # noqa: F401

InputSource = Callable[[], Iterable[Path]]
