"""
Module for locating and accessing [[https://takeout.google.com][Google Takeout]] data
"""

from dataclasses import dataclass
from ..core.common import Paths

from my.config import google as user_config


@dataclass
class google(user_config):
    takeout_path: Paths  # path/paths/glob for the takeout zips


from ..core.cfg import make_config

config = make_config(google)

from pathlib import Path
from typing import Optional, Iterable

from ..core.common import get_files
from ..kython.kompress import kexists

"""
For now, my Google Takeout Structure looks like
pwd; tree -L 2
/home/sean/data/google_takeout
.
└── Takeout-1599315526
    ├── archive_browser.html
    ├── Calendar
    ├── Chrome
    ├── Contacts
    ├── Google Photos
    ├── Google Play Store
    ├── Location History
    ├── My Activity
    └── YouTube and YouTube Music
Currently I'm still figuring this out, exporting manually, storage space
prohibits me from doing this on google drive automatically, so I may just
do this manually every 6 months

Will have to see how merging needs to be done here
"""


def get_takeouts(*, path: Optional[str] = None) -> Iterable[Path]:
    for takeout in get_files(config.takeout_path):
        if path is None or kexists(takeout, path):
            yield takeout


def get_last_takeout(*, path: Optional[str] = None) -> Path:
    # TODO more_itertools?
    matching = list(get_takeouts(path=path))
    return matching[-1]


# TODO might be a good idea to merge across multiple takeouts...
# perhaps even a special takeout module that deals with all of this automatically?
# e.g. accumulate, filter and maybe report useless takeouts?
