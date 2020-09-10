"""
Module for locating and accessing [[https://takeout.google.com][Google Takeout]] data
"""

from dataclasses import dataclass
from typing import Optional
from ..core.common import Paths

from my.config import google as user_config


@dataclass
class google(user_config):
    # directory to unzipped takeout data
    takeout_path: Paths
    # this is the directory that my google drive gets mirrored to locally
    # when it detects a new takeout, it sends a warning, so I can run
    # the script to move it to takeout_path
    # see HPI/scripts/unzip_google_takeout
    google_drive_local_path: Optional[Paths]


from ..core.cfg import make_config

config = make_config(google)

import warnings
from pathlib import Path
from typing import Iterable

from more_itertools import last

from ..core.common import get_files
from ..kython.kompress import kexists


def get_takeouts(*, path: Optional[str] = None) -> Iterable[Path]:
    check_for_new_takeouts()
    for takeout in get_files(config.takeout_path):
        if path is None or kexists(takeout, path):
            yield takeout


def get_last_takeout(*, path: Optional[str] = None) -> Path:
    return last(get_takeouts(path=path))


# if there are any new takeouts, warn me
def check_for_new_takeouts():
    new_takeouts = get_files(config.google_drive_local_path)
    if new_takeouts:
        # this may be temporary, once I'm confident the script works fine over
        # some period, I'll just automate this
        warnings.warn(
            f"Theres a new takeout at {new_takeouts[0]}, run ./scripts/unzip_google_takeout to update the data!"
        )


# TODO might be a good idea to merge across multiple takeouts...
# perhaps even a special takeout module that deals with all of this automatically?
# e.g. accumulate, filter and maybe report useless takeouts?
