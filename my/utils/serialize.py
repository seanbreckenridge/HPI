import os
import uuid
import time
import dataclasses
import datetime
from typing import Any, Optional

import simplejson

# If the date should be formatted to something other than
# the epoch timestamp, set the 'HPI_DATE_FMT' environment
# variable to the format string, like:
# HPI_DATE_FMT='%Y/%m/%d/%H/%M/%S' hpi_query ...
HPI_DATE_FMT: Optional[str] = os.environ.get("HPI_DATE_FMT")


def default_encoder(o: Any) -> Any:
    if isinstance(o, datetime.datetime):
        # encode to epoch time, to remove timezone
        ts: int = int(o.timestamp())
        if HPI_DATE_FMT is None:
            return ts
        else:
            return time.strftime(HPI_DATE_FMT, time.localtime(ts))
    elif isinstance(o, datetime.date):
        # encode to a simpleish to parse datetime
        return o.strftime("%Y/%m/%d")
    elif isinstance(o, datetime.timedelta):
        return int(o.total_seconds())
    elif isinstance(o, uuid.UUID):
        return str(o)
    elif dataclasses.is_dataclass(o):
        return dataclasses.asdict(o)
    raise TypeError(f"{o} of type {type(o)} is not serializable")


def dumps(obj: Any, **kwargs: int) -> str:
    # use simplejson because it handles namedtuples much nicer
    return simplejson.dumps(
        obj, default=default_encoder, namedtuple_as_object=True, **kwargs
    )
