import io
from pathlib import Path
from typing import Iterator

def yield_lines(f: Path) -> Iterator[str]:
    with io.open(f, encoding="latin-1") as fp:
        for line in fp:
            if line.strip() == "":
                continue
            yield line
