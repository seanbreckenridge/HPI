from pathlib import Path
from functools import lru_cache
from typing import Sequence, List

from .common import listify

from .common import LazyLogger

logger = LazyLogger(__name__, level="warning")


@lru_cache
def filesize(p: Path) -> int:
    return p.lstat().st_size


@lru_cache
@listify
def read_prefix(p: Path) -> Sequence[str]:  # type: ignore[misc]
    """
    Read the first 100 lines of a file
    """
    lc = 0
    with p.open("r") as f:
        for line in f:
            lc += 1
            if lc > 100:
                break
            yield line


@lru_cache
def prefix_lines_match(p1: Path, p2: Path) -> bool:
    """
    The first 100 lines of these 2 files match, and size of p1 > p2
    This means we can ignore p2
    """
    if read_prefix(p1) == read_prefix(p2):
        return filesize(p1) > filesize(p2)
    return False


# this improves latency by about 300ms for every backup
# if you had 10 backups, this reduces the time from
# 4 seconds, to 500ms, by preemptively filtering
# duplicates, instead of reading the all in (which uses regex) and
# then removing duplicates
@listify
def filter_subfile_matches(paths: Sequence[Path]) -> Sequence[Path]:  # type: ignore[misc]
    """
    if a file starts with the same 100 lines as another one
    and one file is bigger than another, keep the bigger file

    small optimization to decrease parsing time. Used to history/
    csv files
    """
    sorted_files: List[Path] = sorted(
        paths, key=lambda p: p.lstat().st_size, reverse=True
    )
    unique_files: List[Path] = [sorted_files.pop(0)]
    yield unique_files[0]  # largest file should always be returned
    # for each file were unsure of whether or not its a duplicate
    for s in sorted_files:
        for u in list(unique_files):
            # if the file we havent checked yet,
            # matches a prefix of one of the unique files,
            # ignore it
            if prefix_lines_match(u, s):  # trying to remove 's' from yielded set
                logger.debug(f"Ignoring file: {s}")
            else:
                unique_files.append(s)
                yield s  # this file didnt match, so it maybe from another computer/timeframe
