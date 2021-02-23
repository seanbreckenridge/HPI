"""
Human function things

Interactive prompts to log random things, like my current weight
"""

import os
from pathlib import Path
from itertools import chain
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
from typing import NamedTuple, Iterator, Sequence

from autotui.shortcuts import load_prompt_and_writeback, load_from

from ..core import Stats, get_files
from ..core.core_config import config as core_conf


# creates unique datafiles for each profile (i.e. computer)
def datafile(for_function: str) -> Path:
    profile: str = core_conf.active_profile
    basepath: str = for_function + (f"-{profile}" if profile else "") + ".json"
    return Path(config.datadir).expanduser().absolute() / basepath


# globs all datafiles for every profile for some prefix (for_function)
def glob_json_datafiles(for_function: str) -> Sequence[Path]:
    glob_str = for_function + "*.json"
    return get_files(os.path.expanduser(os.path.join(config.datadir, glob_str)))


class Shower(NamedTuple):
    when: datetime


class Weight(NamedTuple):
    when: datetime
    pounds: float


# These fail if the corresponding files dont exist, log something to the file with the aliases below


def shower() -> Iterator[Shower]:
    yield from chain(
        *map(lambda p: load_from(Shower, p), glob_json_datafiles("shower"))
    )


def weight() -> Iterator[Weight]:
    yield from chain(
        *map(lambda p: load_from(Weight, p), glob_json_datafiles("weight"))
    )


# alias 'shower=python3 -c "from my.body import prompt, Shower; prompt(Shower)"'
# alias 'weight=python3 -c "from my.body import prompt, Weight; prompt(Weight)"'
def prompt(nt: NamedTuple):
    load_prompt_and_writeback(nt, datafile(nt.__name__.casefold()))  # type: ignore[attr-defined]


def stats() -> Stats:
    from ..core import stat

    return {
        **stat(shower),
        **stat(weight),
    }
