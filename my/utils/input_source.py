from pathlib import Path
from typing import Callable, Iterable

InputSource = Callable[[], Iterable[Path]]
