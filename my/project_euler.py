"""
When I completed https://projecteuler.net problems

This information has to be updated manually, I do it once
every few months/years depending on how many of these I keep
solving

To download, log in to your Project Euler account
(in your browser), and then go to:
https://projecteuler.net/history

That txt file is what this accepts as input (can accept multiple)
"""

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import project_euler as user_config  # type: ignore[attr-defined]

from my.core import Paths, dataclass


@dataclass
class config(user_config):
    # path[s]/glob to the .txt export files
    export_path: Paths


import re
from pathlib import Path
from datetime import datetime
from typing import Sequence, Iterator, NamedTuple
from itertools import chain

from more_itertools import unique_everseen

from my.core import get_files, Stats
from .utils.common import InputSource


class Solution(NamedTuple):
    problem: int
    dt: datetime


def project_euler_inputs() -> Sequence[Path]:
    return get_files(config.export_path)


def history(from_paths: InputSource = project_euler_inputs) -> Iterator[Solution]:
    # hmm: maybe someone has multiple accounts and wants to keep track of multiple accounts?
    # If so feel free to make an issue, just doesn't seem like a common use case
    yield from unique_everseen(
        chain(*map(_parse_file, from_paths())), key=lambda s: s.problem
    )


# Example line:
# 037: 07 Nov 14 (13:46)
# project euler was started in early 2000s,
# so no need to support 19XX
# '14' means 2014
LINE_REGEX = re.compile(r"(\d+):\s*(\d+)\s*(\w+)\s*(\d+)\s*\((\d+):(\d+)\)")

# hardcoding instead of using calendar module avoid possible issues with locale
MONTHS = [
    "jan",
    "feb",
    "mar",
    "apr",
    "may",
    "jun",
    "jul",
    "aug",
    "sep",
    "oct",
    "nov",
    "dec",
]


def _parse_file(p: Path) -> Iterator[Solution]:
    for line in p.read_text().strip().splitlines():
        m = LINE_REGEX.match(line)
        if m:
            problem, day, month_desc, year_short, hour, minute = m.groups()
            month_lowered = month_desc.lower()
            assert month_lowered in MONTHS, f"Couldnt find {month_lowered} in {MONTHS}"
            # Note: datetime is naive, so may be different when you downloaded this
            # is different than your current timezone. Could use tz provider and when
            # the file was modified to possibly get which tz to place this into
            yield Solution(
                problem=int(problem),
                dt=datetime(
                    year=int(f"20{year_short}"),
                    month=MONTHS.index(month_lowered) + 1,
                    day=int(day),
                    hour=int(hour),
                    minute=int(minute),
                ),
            )


def stats() -> Stats:
    from my.core import stat

    return {**stat(history)}
