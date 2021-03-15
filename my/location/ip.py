"""
Uses IP address data from other exports to get location data
"""

import ipaddress
from typing import NamedTuple, Iterator
from pathlib import Path
from datetime import datetime
from functools import lru_cache

import ipgeocache

from my.core import Json
from my.core.common import Stats, mcachew, LazyLogger
from my.core.cachew import cache_dir

from .models import Location

from ..facebook import AdminAction, UploadedPhoto
from ..facebook import events as facebook_events
from ..facebook import config as facebook_config
from ..games.blizzard import events as blizzard_events
from ..discord import activity, parse_activity_date
from ..discord import config as discord_config


logger = LazyLogger(__name__, level="warning")


@lru_cache(maxsize=None)
def ipgeocache_mem(addr: str) -> Json:
    return ipgeocache.get(addr)


class IP(NamedTuple):
    dt: datetime
    addr: str

    def ipgeocache(self) -> Json:
        return ipgeocache_mem(self.addr)

    @property
    def location(self) -> Location:
        loc: str = self.ipgeocache()["loc"]
        lat, _, lng = loc.partition(",")
        return Location(
            lat=float(lat),
            lng=float(lng),
            dt=self.dt,
            accuracy=False,
        )

    # ipgeocache returns timezone info as well!
    @property
    def tz(self) -> str:
        return self.ipgeocache()["timezone"]


def ips() -> Iterator[IP]:
    yield from _from_facebook()
    yield from _from_blizzard()
    yield from _from_discord()


@mcachew(
    cache_path=cache_dir(),
    depends_on=lambda: list(map(str, Path(facebook_config.gdpr_dir).rglob("*"))),
    logger=logger,
)
def _from_facebook() -> Iterator[IP]:
    for e in facebook_events():
        if isinstance(e, AdminAction) or isinstance(e, UploadedPhoto):
            if not isinstance(e, Exception):
                yield IP(dt=e.dt, addr=e.ip)


@mcachew(cache_path=cache_dir(), logger=logger)
def _from_blizzard() -> Iterator[IP]:
    for e in blizzard_events():
        if e.event_tag == "Activity History":
            yield IP(dt=e.dt, addr=e.metadata[-2])


@mcachew(
    cache_path=cache_dir(), depends_on=lambda: discord_config.latest(), logger=logger
)
def _from_discord() -> Iterator[IP]:
    for a in activity():
        if "ip" in a:
            # for some reason returns some IPs that are using the private address space??
            if not ipaddress.ip_address(a["ip"]).is_private:
                yield IP(dt=parse_activity_date(a["timestamp"]), addr=a["ip"])


def stats() -> Stats:
    from my.core import stat

    return {
        **stat(ips),
    }
