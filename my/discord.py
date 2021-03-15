"""
Discord Data: messages and events data
"""
REQUIRES = [
    "git+https://github.com/seanbreckenridge/discord_data",
]


from pathlib import Path

from my.config import discord as user_config  # type: ignore[attr-defined]
from my.core import PathIsh, dataclass


@dataclass
class config(user_config):

    # path[s]/glob to the exported JSON data
    export_path: PathIsh

    # TODO: replace with inputs()?
    @classmethod
    def latest(cls) -> Path:
        non_hidden = [
            p for p in get_files(cls.export_path) if not p.name.startswith(".")
        ]
        return sorted(non_hidden, key=lambda p: p.stat().st_ctime)[-1]


from typing import Iterator
from datetime import datetime, timezone
from my.core.common import get_files, LazyLogger, Stats, mcachew
from my.core.cachew import cache_dir

from discord_data import parse_activity, parse_messages
from discord_data.model import Message, Json


logger = LazyLogger(__name__, level="warning")


# reduces time by half, after cache is created
@mcachew(depends_on=lambda: config.latest(), cache_path=cache_dir(), logger=logger)
def messages() -> Iterator[Message]:
    yield from parse_messages(config.latest() / "messages")


# not worth putting behind cachew, just loading Json
def activity() -> Iterator[Json]:
    yield from parse_activity(config.latest() / "activity", logger=logger)


def parse_activity_date(s: str) -> datetime:
    # assuming this is UTC
    return datetime.astimezone(
        datetime.fromisoformat(s.strip('"').rstrip("Z")), tz=timezone.utc
    )


def stats() -> Stats:
    from my.core import stat

    return {
        **stat(messages),
        **stat(activity),
    }
