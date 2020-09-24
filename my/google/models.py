from datetime import datetime
from typing import List, NamedTuple, Tuple

Metadata = Tuple[str, str]  # key-value pair from html caption


# need to do some analysis on the metadata/links once its all parsed
# to see if it can be simplified into an ADT which doesnt have
# variant lists
#
# perhaps this should be encoded into another namedtuple, becuase it takes
# a sizable amount of time to parse the HTMl pages, would really benifit
# from cachew
class HtmlEvent(NamedTuple):
    service: str
    desc: str
    metadata: List[Metadata]
    links: List[str]
    at: datetime


class HtmlComment(NamedTuple):
    desc: str
    links: List[str]
    at: datetime


# not sure about this namedtuple structure
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
    at: datetime


class AppInstall(NamedTuple):
    title: str
    at: datetime


class Location(NamedTuple):
    lng: float
    lat: float
    at: datetime
