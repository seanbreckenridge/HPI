from datetime import datetime
from typing import NamedTuple, Iterator

from autotui.shortcuts import load_from

# just re-use the datadir info from the my.body module
from ..body import datafile


class Water(NamedTuple):
    when: datetime
    glasses: float


def water() -> Iterator[Water]:
    yield from load_from(Water, datafile("water"))
