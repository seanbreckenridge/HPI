import json
from datetime import datetime
from typing import Any, NamedTuple, Optional
from dataclasses import dataclass


# to make this cachew compliant
def _parse_json_attr(el, attr: str):
    json_str: str = getattr(el, attr)
    json_obj: Any = json.loads(json_str)
    setattr(el, attr, json_obj)


@dataclass
class HtmlEvent:
    service: str
    desc: str
    at: datetime
    product_name: Optional[str]
    # json serialized arrays/objects
    links: str

    # called after imported into repl, to convert back to the python objects
    def parse_json(self):
        _parse_json_attr(self, "links")


@dataclass
class HtmlComment:
    desc: str
    at: datetime
    # json serialized arrays
    links: str

    def parse_json(self):
        _parse_json_attr(self, "links")


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
