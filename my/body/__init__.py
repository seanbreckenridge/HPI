"""
Human function things

Interactive prompts to log random things, like when I brush teeth/current weight etc.
"""

from pathlib import Path
from dataclasses import dataclass

from ..core import PathIsh

# https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py
from my.config import body as user_config


@dataclass
class upkeep(user_config):
    datadir: PathIsh


from ..core.cfg import make_config

config = make_config(upkeep)

from datetime import datetime
from typing import NamedTuple, Iterator

from autotui.shortcuts import load_prompt_and_writeback, load_from

from ..core import Stats


def datafile(for_function: str) -> Path:
    return Path(config.datadir).expanduser().absolute() / f"{for_function}.json"


class Teeth(NamedTuple):
    when: datetime


class Shower(NamedTuple):
    when: datetime


class Weight(NamedTuple):
    when: datetime
    pounds: float


# These fail if the corresponding files dont exist, log something to the file with the aliases below
def teeth() -> Iterator[Teeth]:
    yield from load_from(Teeth, datafile("teeth"))


def shower() -> Iterator[Shower]:
    yield from load_from(Shower, datafile("shower"))


def weight() -> Iterator[Weight]:
    yield from load_from(Weight, datafile("weight"))


# alias 'teeth=python3 -c "from my.body import prompt, Teeth; prompt(Teeth)"'
# alias 'shower=python3 -c "from my.body import prompt, Shower; prompt(Shower)"'
# alias 'weight=python3 -c "from my.body import prompt, Weight; prompt(Weight)"'
def prompt(nt: NamedTuple):
    load_prompt_and_writeback(nt, datafile(nt.__name__.casefold()))  # type: ignore[attr-defined]


def stats() -> Stats:
    from ..core import stat

    return {
        **stat(teeth),
        **stat(shower),
        **stat(weight),
    }
