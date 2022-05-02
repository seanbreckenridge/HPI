from typing import Union
from datetime import datetime, timezone

from my.core import __NOT_HPI_MODULE__  # noqa: F401

# TODO: maybe this should be PR'd to master/put into
# my.time.tz/utils?


def parse_datetime_sec(d: Union[str, float, int]) -> datetime:
    return datetime.fromtimestamp(int(d), tz=timezone.utc)


def parse_datetime_millis(d: Union[str, float, int]) -> datetime:
    return parse_datetime_sec(int(d) / 1000)
