"""
Parses my Google Takeout using https://github.com/seanbreckenridge/google_takeout_parser
"""

REQUIRES = ["git+https://github.com/seanbreckenridge/google_takeout_parser"]

import os
from typing import List
from pathlib import Path
from my.core import make_config, dataclass
from my.core.common import Stats, LazyLogger, mcachew, get_files, Paths
from my.core.structure import match_structure

from google_takeout_parser.path_dispatch import TakeoutParser, Results
from google_takeout_parser.merge import GoogleEventSet

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import google as user_config


@dataclass
class google(user_config):
    # directory to unzipped takeout data
    takeout_path: Paths


config = make_config(google)


logger = LazyLogger(__name__, level="warning")

# patch TAKEOUT_LOGS to match HPI_LOGS
if "HPI_LOGS" in os.environ:
    from google_takeout_parser.log import setup as setup_takeout_logger
    from my.core.logging import mklevel

    setup_takeout_logger(mklevel(os.environ["HPI_LOGS"]))


def inputs() -> List[Path]:
    return list(get_files(config.takeout_path))


def _cachew_depends_on() -> List[str]:
    return sorted([str(p) for p in inputs()])


EXPECTED = "My Activity"


@mcachew(depends_on=_cachew_depends_on, logger=logger, force_file=True)
def events() -> Results:
    emitted = GoogleEventSet()
    # reversed shouldn't really matter? but logic is to use newer
    # takeouts if they're named according to date, since JSON Activity
    # is nicer than HTML Activity
    for path in reversed(inputs()):
        with match_structure(path, expected=EXPECTED) as results:
            for m in results:
                # e.g. /home/sean/data/google_takeout/Takeout-1634932457.zip") -> 'Takeout-1634932457'
                # means that zipped takeouts have nice filenames from cachew
                cw_id, _, _ = path.name.rpartition(".")
                for event in TakeoutParser(m, cachew_identifier=cw_id).cached_parse():
                    if isinstance(event, Exception):
                        continue
                    if event in emitted:
                        continue
                    emitted.add(event)
                    yield event


def stats() -> Stats:
    from my.core import stat

    return {
        **stat(events),
    }
