"""
Parses achievement data/timestamps from local minecraft worlds
Copied from the ~/.minecraft directory, one for each world
Backed up with:
https://github.com/seanbreckenridge/HPI-personal/blob/master/scripts/backup_minecraft_advancements
"""

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import minecraft as user_config  # type: ignore[attr-defined]

from my.core import Paths, dataclass


@dataclass
class config(user_config.advancements):
    # path[s]/glob to the backup directory
    export_path: Paths


import json
from pathlib import Path
from typing import Sequence, NamedTuple, Iterator, List, Any, Dict
from datetime import datetime
from itertools import chain

from my.core import get_files, Stats
from my.core.structure import match_structure
from my.utils.input_source import InputSource

from more_itertools import unique_everseen

EXPECTED = ("advancements",)


def _advancement_json_files(world_dir: Path) -> List[Path]:
    d = (world_dir / "advancements").absolute()
    if not d.exists():
        return []
    return list(d.rglob("*.json"))


def worlds() -> Sequence[Path]:
    found = []
    for f in get_files(config.export_path):
        with match_structure(f, EXPECTED) as match:
            for m in match:
                if _advancement_json_files(m):
                    found.append(m.absolute())
    return found


class Advancement(NamedTuple):
    advancement_id: str
    world_name: str
    dt: datetime


Results = Iterator[Advancement]


def advancements(for_worlds: InputSource = worlds) -> Results:
    yield from unique_everseen(chain(*map(_parse_world, for_worlds())))


DATE_REGEX = r"%Y-%m-%d %H:%M:%S %z"


def _parse_world(world_dir: Path) -> Results:
    """
    An example of a key, val this is trying to parse:

      "minecraft:nether/obtain_crying_obsidian": {
        "criteria": {
          "crying_obsidian": "2022-06-17 22:48:18 -0700"
        },
        "done": true
      },
    """

    for f in _advancement_json_files(world_dir):
        data = json.loads(f.read_text())
        for key, val in data.items():
            # ignore advances in 'can craft things'
            if key.startswith("minecraft:recipes"):
                continue
            if not isinstance(val, dict):
                continue
            if "done" in val:
                if val["done"] is False:
                    continue
            possible_date_blobs: List[Dict[Any, Any]] = [
                v for v in val.values() if isinstance(v, dict)
            ]
            for blob in possible_date_blobs:
                for datestr in filter(lambda s: isinstance(s, str), blob.values()):
                    try:
                        parsed_date = datetime.strptime(datestr, DATE_REGEX)
                    except ValueError:
                        continue
                    yield Advancement(
                        advancement_id=key, world_name=world_dir.stem, dt=parsed_date
                    )


def stats() -> Stats:
    from my.core import stat

    return {**stat(advancements)}
