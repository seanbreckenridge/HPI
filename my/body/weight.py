"""
Weight data (manually logged)
"""

import csv

from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import NamedTuple, Iterator, Optional

from ..core import PathIsh
from ..core.error import Res

from my.config import weight as user_config


@dataclass
class weight(user_config):
    # csv file with utc date, weight
    logfile: PathIsh

    @property
    def file(self) -> Optional[Path]:
        """
        Warn the user if the logfile doesnt exist, else return the absolute path
        """
        p: Path = Path(self.logfile).expanduser().absolute()
        if not p.exists():
            import warnings

            warnings.warn(f"weight: {p} does not exist")
            return
        else:
            return p


from ..core.cfg import make_config

config = make_config(weight)


class Entry(NamedTuple):
    dt: datetime
    value: float

    def write(self):
        """Write the entry to the CSV log file"""
        with open(config.file, "a", newline="") as csv_file:
            csv_writer = csv.writer(csv_file, delimiter="|", quoting=csv.QUOTE_MINIMAL)
            # converts to epoch seconds in UTC
            csv_writer.writerow([int(self.dt.timestamp()), self.value])


Result = Res[Entry]


def history() -> Iterator[Result]:
    with open(config.file, "r", newline="") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter="|", quoting=csv.QUOTE_MINIMAL)
        for line in csv_reader:
            try:
                dt_str, val_str = line
                # returns date in UTC time
                # TODO: maybe make these all explicit using pytz and tz= ... or arrow? or set a global timezone for the DAL?
                yield Entry(
                    dt=datetime.utcfromtimestamp(int(dt_str)), value=float(val_str)
                )
            except Exception as e:
                yield e
