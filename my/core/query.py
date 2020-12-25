import inspect
import importlib
import datetime
from types import FunctionType
from typing import TypeVar, Optional, Any, Union, Callable, Iterator

from more_itertools import peekable


class QueryException(KeyError):
    pass


def find_hpi_function(module_name: str, function_name: str) -> FunctionType:
    try:
        modval = importlib.import_module(module_name)
        for (fname, func) in inspect.getmembers(modval, inspect.isfunction):
            if fname == function_name:
                return func
    except Exception as e:
        raise QueryException(str(e))
    raise QueryException(
        "Could not find function {} in {}".format(function_name, module_name)
    )


T = TypeVar("T")
DateLike = Union[datetime.datetime, datetime.date]
DateFunc = Callable[[T], DateLike]


def datefunc(obj: T) -> Optional[DateFunc]:
    """
    Accepts an object T. Attempts to find a date-like value on the object,
    using some getattr/dict checks. Returns a function which when called with
    this object returns the date
    """
    if isinstance(obj, dict):
        for key, val in obj.items():
            if isinstance(val, datetime.datetime) or isinstance(val, datetime.date):
                return lambda o: o[key]  # type: ignore[index]
        else:
            return None
    # if not dict, try to use getattr
    for key in [x for x in dir(obj) if not x.startswith("_")]:
        attrval: Any = getattr(obj, key)
        if isinstance(attrval, datetime.datetime) or isinstance(attrval, datetime.date):
            return lambda o: getattr(o, key)
    return None


# given any stream of events, order it by date
def order_by_date(
    res: Iterator[T], reverse: bool = False, dfunc: Optional[DateFunc] = None
) -> Iterator[T]:
    if dfunc is None:
        res = peekable(res)
        dfunc = datefunc(res.peek())
    if dfunc is None:
        return
    yield from sorted(res, key=dfunc, reverse=reverse)


# check that this events date is within the range described
def within_range(
    current: datetime.datetime, event_date: DateLike, time_range: datetime.timedelta
) -> bool:
    time_secs: int = int(time_range.total_seconds())
    current_secs: int = int(current.timestamp())
    event_secs: int = 0
    if isinstance(event_date, datetime.date):
        event_secs = int(
            datetime.datetime.combine(
                event_date, datetime.datetime.min.time()
            ).timestamp()
        )
    else:
        event_secs = int(event_date.timestamp())
    return current_secs - event_secs < time_secs


def most_recent(
    res: Iterator[T],
    events: Union[int, bool] = 250,
    time_range: Union[datetime.timedelta, bool] = datetime.timedelta(days=30),
) -> Iterator[T]:
    """
    retrieve the most recent 'n' events or within the
    timerange given
    Lets me grab events very easily:
    import my.core.query as qr
      list(qr.most_recent(qr.find_hpi_function("my.food", "food")()))
      list(qr.most_recent(qr.find_hpi_function("my.zsh", "history")()))
    If 'True' is provided as events or time_range, acts as infinite
    """
    # special case, to avoid all the computation
    if events is True and time_range is True:
        yield from order_by_date(res, reverse=True)
        return

    count: int = 0
    res = peekable(res)
    dfunc: Optional[DateFunc] = datefunc(res.peek())
    if dfunc is None:
        return

    current: datetime.datetime = datetime.datetime.now()

    for evnt in order_by_date(res, reverse=True, dfunc=dfunc):
        if time_range is True or (
            isinstance(time_range, datetime.timedelta)
            and within_range(current, dfunc(evnt), time_range)
        ):
            yield evnt
        else:
            break
        if events is True:
            continue
        else:
            count += 1
            if count >= events:
                break
