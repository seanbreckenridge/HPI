"""
Human function things

Interactive prompts to log random things, like my current weight
"""

REQUIRES = [
    "git+https://github.com/seanbreckenridge/tupletally",
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


from typing import Iterator
from functools import partial
from tupletally.autotui_ext import glob_namedtuple
from tupletally.config import Weight, Shower  # type: ignore[attr-defined]

glob_namedtuple_with_config = partial(glob_namedtuple, in_dir=config.abs())


def weight() -> Iterator[Weight]:
    yield from glob_namedtuple_with_config(Weight)


def shower() -> Iterator[Shower]:
    yield from glob_namedtuple_with_config(Shower)


def stats() -> Stats:
    from my.core import stat

    return {
        **stat(shower),
        **stat(weight),
    }
