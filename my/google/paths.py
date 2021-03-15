"""
Module for locating and accessing [[https://takeout.google.com][Google Takeout]] data
"""

from typing import Optional

# note: doesn't match definition of karlicoss/HPI google config
from my.config import google as user_config
from my.core import Paths, dataclass


@dataclass
class google(user_config):
    # directory to unzipped takeout data
    takeout_path: Paths
    # this is the directory that my google drive gets mirrored to locally
    # when it detects a new takeout, it sends a warning, so I can run
    # the script to move it to takeout_path
    # see HPI/scripts/unzip_google_takeout
    google_drive_local_path: Optional[str]


# leave make_config, because its likely I may need a migration here/stuff may change
from my.core.cfg import make_config

config = make_config(google)

from pathlib import Path
from typing import Iterable, List

from more_itertools import last

from my.core import get_files
from my.core.warnings import low
from my.core.kompress import kexists


def get_takeouts(*, path: Optional[str] = None) -> Iterable[Path]:
    check_for_new_takeouts()
    for takeout in get_files(config.takeout_path):
        if path is None or kexists(takeout, path):
            yield takeout


def get_last_takeout(*, path: Optional[str] = None) -> Path:
    return last(get_takeouts(path=path))


# if there are any new takeouts, warn me
def check_for_new_takeouts():
    if config.google_drive_local_path:
        p = Path(config.google_drive_local_path).expanduser().absolute()
        new_takeouts: List[Path] = list(p.rglob("*"))
        if new_takeouts:
            # this may be temporary, once I'm confident the script works fine over
            # some period, I'll just automate this
            low(
                f"Theres a new takeout at {new_takeouts[0]}, run ./scripts/unzip_google_takeout to update the data!"
            )
