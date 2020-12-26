import uuid
import dataclasses
import datetime
import simplejson
from typing import Any


def default_encoder(o: Any) -> Any:
    if isinstance(o, datetime.datetime):
        # encode to epoch time
        return int(o.timestamp())
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
