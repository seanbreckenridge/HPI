"""
Discord Data: messages and events data
"""
REQUIRES = [
    "git+https://github.com/seanbreckenridge/discord_data",
]

from .core.common import PathIsh

from my.config import discord as uconfig
from dataclasses import dataclass


@dataclass
class discord(uconfig):

    # path[s]/glob to the exported JSON data
    export_path: PathIsh

    @property
    def latest(self):
        return get_files(self.export_path)[-1]


from .core.cfg import make_config


config = make_config(discord)


from typing import Iterator
from .core.common import get_files, LazyLogger, Stats

from discord_data import parse_activity, parse_messages
from discord_data.model import Message, Json


logger = LazyLogger(__name__, level="warning")


# cache = mcachew(depends_on=lambda: list(get_files(config.export_path)), cache_path=cache_dir())
# @cache()


def messages() -> Iterator[Message]:
    yield from parse_messages(config.latest / "messages")


def activity() -> Iterator[Json]:
    yield from parse_activity(config.latest / "activity", logger=logger)


def stats() -> Stats:
    from .core import stat

    return {
        **stat(messages),
        **stat(activity),
    }
