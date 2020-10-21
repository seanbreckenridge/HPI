"""
Uses IP address data from other exports to get location data
"""

from typing import NamedTuple, Iterator
from datetime import datetime
from itertools import chain

import ipgeocache

from .models import LatLon
from ..facebook import AdminAction, UploadedPhoto
from ..facebook import events as facebook_events

from ..games.blizzard import events as blizzard_events


class IP(NamedTuple):
    at: datetime
    addr: str

    def ipgeocache_info(self) -> ipgeocache.Json:
        return ipgeocache.get(self.addr)

    @property
    def location(self) -> LatLon:
        loc: str = self.ipgeocache_info()["loc"]
        lat, _, lon = loc.partition(",")
        return (float(lat), float(lon))

    # ipgeocache returns timezone info as well!
    @property
    def tz(self) -> str:
        return self.ipgeocache_info()["timezone"]


def ips() -> Iterator[IP]:
    yield from sorted(
        chain(
            _from_facebook(),
            _from_blizzard(),
        ),
        key=lambda i: i.at,
    )


def _from_facebook() -> Iterator[IP]:
    yield from map(
        lambda i: IP(at=i.at, addr=i.ip),
        filter(
            lambda e: isinstance(e, AdminAction) or isinstance(e, UploadedPhoto),
            facebook_events(),
        ),
    )


def _from_blizzard() -> Iterator[IP]:
    yield from map(
        lambda i: IP(at=i.dt, addr=i.metadata[-2]),
        filter(lambda e: e.event_tag == "Activity History", blizzard_events()),
    )
