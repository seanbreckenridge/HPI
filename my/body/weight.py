"""
Weight data (manually logged)
"""

from datetime import datetime
from dataclasses import dataclass
from typing import NamedTuple, Iterator

from ..core import PathIsh

from my.config import weight as user_config

from autotui.shortcuts import load_prompt_and_writeback, load_from


@dataclass
class weight(user_config):
    datafile: PathIsh


from ..core.cfg import make_config

config = make_config(weight)


class Weight(NamedTuple):
    when: datetime
    pounds: float


Result = Iterator[Weight]


def history() -> Result:
    # fails if the file doesnt exist
    yield from load_from(Weight, config.datafile)


def stats():
    from ..core import stat

    return {**stat(history)}


# alias 'weight=python3 -c "from my.body.weight import prompt; prompt()"'
def prompt():
    load_prompt_and_writeback(Weight, config.datafile)
