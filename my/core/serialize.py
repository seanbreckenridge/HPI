import uuid
import dataclasses
import datetime
import simplejson
from typing import Any


def default_encoder(o: Any) -> Any:
    """
    Note:
    Instead of trying to parse into something like RFC3339,
    just parse a datetime/date into a List, and tag it
    with a special tag '_TIME_' and '_DATE_',
    """
    if isinstance(o, datetime.datetime):
        # encode to epoch time
        return ["_TIME_", int(o.timestamp())]
    elif isinstance(o, datetime.date):
        # encode to a simpleish to parse datetime
        return ["_DATE_", o.strftime("%Y/%m/%d")]
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
