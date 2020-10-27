from datetime import date, datetime
from typing import Union, Tuple, NamedTuple

DateIsh = Union[datetime, date, str]

# todo hopefully reasonable? might be nice to add name or something too
LatLon = Tuple[float, float]


class Location(NamedTuple):
    lng: float
    lat: float
    dt: datetime
    # approximate accuracy
    # true means exact, false means its based on ip/auxillary info
    accuracy: bool
