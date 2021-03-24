"""
Discord Data: messages and events data
"""
REQUIRES = [
    "git+https://github.com/seanbreckenridge/discord_data",
]


from pathlib import Path
from typing import List

from my.config import discord as user_config  # type: ignore[attr-defined]
from my.core import PathIsh, dataclass


@dataclass
class config(user_config):

    # path to the top level discord export directory
    # see https://github.com/seanbreckenridge/discord_data for more info
    export_path: PathIsh

    # property? functools.cached_property?
    @classmethod
    def _abs_export_path(cls) -> Path:
        return Path(cls.export_path).expanduser().absolute()


from typing import Iterator
from my.core.common import LazyLogger, Stats, mcachew
from my.core.cachew import cache_dir

from discord_data import merge_messages, merge_activity, Message, Activity


logger = LazyLogger(__name__, level="warning")


def _cachew_depends_on() -> List[str]:
    return list(map(str, config._abs_export_path().iterdir()))


# reduces time by half, after cache is created
@mcachew(depends_on=_cachew_depends_on, cache_path=cache_dir(), logger=logger)
def messages() -> Iterator[Message]:
    yield from merge_messages(export_dir=config._abs_export_path())


@mcachew(depends_on=_cachew_depends_on, cache_path=cache_dir(), logger=logger)
def activity() -> Iterator[Activity]:
    yield from merge_activity(export_dir=config._abs_export_path())


def stats() -> Stats:
    from my.core import stat

    return {
        **stat(messages),
        **stat(activity),
    }
