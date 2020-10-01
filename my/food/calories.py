"""
Exports info from https://github.com/zupzup/calories
"""

import json
import shutil
import subprocess

from datetime import datetime, date
from typing import NamedTuple, Iterator, Optional, Dict, Any

from ..core.error import Res

calories_path: Optional[str] = shutil.which("calories")
if calories_path is None:
    raise RuntimeError("Couldn't find 'calories' on your $PATH")

Json = Dict[str, Any]


class Food(NamedTuple):
    on: date
    calories: float
    name: str


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
            calories=float(cal["calories"]),
            name=cal["food"].strip(),
        )
