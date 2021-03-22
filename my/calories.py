"""
Exports info from https://github.com/zupzup/calories
"""

import json
import shutil
import subprocess

from datetime import datetime, date
from typing import NamedTuple, Iterator, Optional

from my.core import Res, Json, Stats

calories_path: Optional[str] = shutil.which("calories")
if calories_path is None:
    raise RuntimeError("Couldn't find 'calories' on your $PATH")


# on is the date which this entry is for, added_on is a timestamp which matches
# exactly when I added it
class Food(NamedTuple):
    on: date
    added_on: datetime
    calories: float
    name: str


# TODO: parse AMR? (number of calories my body should burn each day)


def food() -> Iterator[Res[Food]]:
    proc: subprocess.CompletedProcess = subprocess.run(
        [calories_path, "export"],  # type: ignore[list-item]
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    proc_output: str = proc.stdout.strip()
    if proc.returncode != 0:
        yield RuntimeError(proc_output)
        return
    try:
        json_cals: Json = json.loads(proc_output)
    except json.JSONDecodeError as je:
        yield je
        return

    for cal in json_cals["entries"]:
        yield Food(
            on=datetime.strptime(cal["entryDate"], "%d.%m.%Y").date(),
            added_on=_truncate_iso_date(cal["created"]),
            calories=float(cal["calories"]),
            name=cal["food"].strip(),
        )


def _truncate_iso_date(dstr: str) -> datetime:
    """
    Remove the decimal points 'manually' and then parse using fromisoformat
    2020-12-25T07:44:14.32152639-08:00 -> 2020-12-25T07:44:14-08:00 -> fromisoformat -> datetime obj
    """
    buf = ""
    incl = True
    for c in dstr:
        if c == ".":
            incl = False
        if c == "-":
            incl = True
        if incl:
            buf += c
    return datetime.fromisoformat(buf)


def stats() -> Stats:
    from my.core import stat

    return {**stat(food)}
