# alias 'water=python3 -c "from my.food import prompt, Water; prompt(Water)"'
# alias 'water-now=python3 -c "from my.food.water import water_now; water_now()"'

from datetime import datetime
from pathlib import Path
from typing import NamedTuple, Iterator, List

from autotui.shortcuts import load_from, dump_to

# just re-use the datadir info from the my.body module
from ..body import datafile


class Water(NamedTuple):
    when: datetime
    glasses: float


def water() -> Iterator[Water]:
    yield from load_from(Water, datafile("water"))


def water_now():
    """
    An alternative to the autotui interface, to add water *now*
    Defaults to now, 1 glass of water. provide a float as the first argument
    to override
    """
    import sys

    glasses_count: float = 1.0
    try:
        glasses_count = float(sys.argv[1])
    except IndexError:
        pass
    except ValueError:
        print("Could not convert '{}' to a float".format(sys.argv[1]), file=sys.stderr)
        raise SystemExit(1)

    # load water
    water_f: Path = datafile("water")
    items: List[Water] = load_from(Water, water_f)

    items.append(Water(when=datetime.now(), glasses=glasses_count))
    print(items[-1])
    dump_to(items, water_f)
