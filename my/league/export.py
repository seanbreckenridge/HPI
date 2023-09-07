"""
Parses league of legend history from https://github.com/seanbreckenridge/lolexport
"""

REQUIRES = ["git+https://github.com/seanbreckenridge/lolexport"]


# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import league as user_config  # type: ignore[attr-defined]
from my.core import Paths, dataclass


@dataclass
class config(user_config.export):
    # path[s]/glob to the exported data. These are the resulting json file from 'lolexport parse', or v5 exports
    export_path: Paths

    # league of legends username
    username: str


from pathlib import Path
from typing import Iterator, Sequence, Optional

from my.core import get_files, Stats, Res, make_logger
from my.utils.input_source import InputSource

from lolexport.merge import Game, merge_game_histories
import lolexport.log as llog
from logzero import setup_logger  # type: ignore[import]

logger = make_logger(__name__)

# configure logs
llog.logger = setup_logger(name="lolexport", level=logger.level)


def inputs() -> Sequence[Path]:
    return get_files(config.export_path)


Results = Iterator[Res[Game]]


def history(
    from_paths: InputSource = inputs, summoner_name: Optional[str] = None
) -> Results:
    sname = summoner_name or config.username
    for g in merge_game_histories(list(from_paths()), username=sname):
        try:
            g._serialize()  # try parsing the data from this
            yield g
        except Exception as ex:
            yield ex


def stats() -> Stats:
    from my.core import stat

    return {**stat(history)}
