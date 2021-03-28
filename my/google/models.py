import json
from datetime import datetime
from typing import NamedTuple, Optional, List


class HtmlEvent(NamedTuple):
    service: str
    desc: str
    dt: datetime
    product_name: Optional[str]
    links: List[str]


class HtmlComment(NamedTuple):
    desc: str
    dt: datetime
    links: List[str]


# not sure about this namedtuple/dataclass structure
# makes it nicer when Im trying to extract a particular
# item, but harder to work with on a broad scale
# maybe implement some @property wrappers
# for common structure? or
# inherit from a base namedtuple
# that does some hasattr hackery


class LikedVideo(NamedTuple):
    title: str
    desc: str
    link: str
    dt: datetime


class AppInstall(NamedTuple):
    title: str
    dt: datetime


class Location(NamedTuple):
    lng: float
    lat: float
    dt: datetime
