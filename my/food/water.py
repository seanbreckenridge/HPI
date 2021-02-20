# alias 'water=python3 -c "from my.food import prompt, Water; prompt(Water)"'
# alias 'water-now=python3 -c "from my.food.water import water_now; water_now()"'

from datetime import datetime
from pathlib import Path
from typing import NamedTuple, Iterator, List

from autotui.shortcuts import load_from, dump_to
from bash_like import S, SO

# just re-use the datadir info from the my.body module
from ..body import datafile, glob_json_datafiles, chain


class Water(NamedTuple):
    when: datetime
    glasses: float


def water() -> Iterator[Water]:
    yield from chain(*map(lambda p: load_from(Water, p), glob_json_datafiles("water")))


def water_now():
    """
    An alternative to the autotui interface, to add water *now*
    Defaults to now, 1 glass of water. provide a float as the first argument
    to override
    """
    import sys

    try:
        glasses_count: float = float(SO - (1, 1.0))
    except ValueError:
        S(f"Could not convert '{sys.argv[1]}' to a float\n") > 2
        raise SystemExit(1)

    # load water
    water_f: Path = datafile("water")
    items: List[Water] = load_from(Water, water_f)

    items.append(Water(when=datetime.now(), glasses=glasses_count))
    print(items[-1])
    dump_to(items, water_f)
