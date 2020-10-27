"""
Uses IP address data from other exports to get location data
"""

import ipaddress
from typing import NamedTuple, Iterator
from pathlib import Path
from datetime import datetime
from functools import lru_cache

import ipgeocache

from ..core.common import Stats, mcachew, LazyLogger
from ..core.cachew import cache_dir

from .models import Location

from ..facebook import AdminAction, UploadedPhoto
from ..facebook import events as facebook_events
from ..facebook import config as facebook_config
from ..games.blizzard import events as blizzard_events
from ..discord import activity, parse_activity_date
from ..discord import config as discord_config


logger = LazyLogger(__name__, level="warning")


@lru_cache(maxsize=None)
def ipgeocache_mem(addr: str) -> ipgeocache.Json:
    return ipgeocache.get(addr)


class IP(NamedTuple):
    at: datetime
    addr: str

    def ipgeocache(self) -> ipgeocache.Json:
        return ipgeocache_mem(self.addr)

    @property
    def location(self) -> Location:
        loc: str = self.ipgeocache()["loc"]
        lat, _, lng = loc.partition(",")
        return Location(
            lat=float(lat),
            lng=float(lng),
            dt=self.at,
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
    yield from map(
        lambda i: IP(at=i.at, addr=i.ip),
        filter(
            lambda e: isinstance(e, AdminAction) or isinstance(e, UploadedPhoto),
            facebook_events(),
        ),
    )


@mcachew(cache_path=cache_dir(), logger=logger)
def _from_blizzard() -> Iterator[IP]:
    yield from map(
        lambda i: IP(at=i.dt, addr=i.metadata[-2]),
        filter(lambda e: e.event_tag == "Activity History", blizzard_events()),
    )


@mcachew(
    cache_path=cache_dir(), depends_on=lambda: discord_config.latest, logger=logger
)
def _from_discord() -> Iterator[IP]:
    for a in activity():
        if "ip" in a:
            # for some reason returns some IPs that are using the private address space??
            if not ipaddress.ip_address(a["ip"]).is_private:
                yield IP(at=parse_activity_date(a["timestamp"]), addr=a["ip"])


def stats() -> Stats:
    from ..core import stat

    return {
        **stat(ips),
    }
