from functools import lru_cache
from datetime import datetime, tzinfo, timezone
from typing import Union

import pytz  # type: ignore

# https://gist.github.com/edwardabraham/8680198
tz_lookup = {
    pytz.timezone(x).localize(datetime.now()).tzname(): pytz.timezone(x)
    for x in pytz.all_timezones
}
tz_lookup["UTC"] = pytz.utc  # ugh. otherwise it'z Zulu...
tz_lookup["PDT"] = tz_lookup["PST"]


# TODO dammit, lru_cache interferes with mypy?
@lru_cache(None)
def abbr_to_timezone(abbr: str) -> tzinfo:
    return tz_lookup[abbr]


def parse_datetime_sec(d: Union[str, float, int]) -> datetime:
    return datetime.fromtimestamp(int(d), tz=timezone.utc)


def parse_datetime_millis(d: Union[str, float, int]) -> datetime:
    return parse_datetime_sec(int(d) / 1000)
