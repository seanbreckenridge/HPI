"""
Human function things

Interactive prompts to log random things, like my current weight
"""

REQUIRES = [
    "git+https://github.com/seanbreckenridge/ttally",
]

from pathlib import Path

# https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py
from my.config import body as user_config  # type: ignore[attr-defined]
from my.core import PathIsh, dataclass, Stats


@dataclass
class config(user_config):
    datadir: PathIsh

    @classmethod
    def abs(cls) -> Path:
        return Path(cls.datadir).expanduser().absolute()


from typing import Iterator, NamedTuple
from functools import partial
from datetime import datetime

from ttally.autotui_ext import glob_namedtuple

# for definitions see https://sean.fish/d/ttally.py
from ttally.config import Weight, Shower, Food  # type: ignore[attr-defined]

glob_namedtuple_with_config = partial(glob_namedtuple, in_dir=config.abs())


def weight() -> Iterator[Weight]:
    yield from glob_namedtuple_with_config(Weight)


def shower() -> Iterator[Shower]:
    yield from glob_namedtuple_with_config(Shower)


def food() -> Iterator[Food]:
    yield from glob_namedtuple_with_config(Food)


class Water(NamedTuple):
    when: datetime
    ml: float


# extracts from the water attribute on food
def water() -> Iterator[Water]:
    for f in food():
        ml = f.quantity * f.water
        if ml > 0:
            yield Water(when=f.when, ml=ml)


def stats() -> Stats:
    from my.core import stat

    return {
        **stat(shower),
        **stat(weight),
        **stat(food),
        **stat(water),
    }
