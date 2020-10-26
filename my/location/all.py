"""
Merges location data from multiple sources
"""

from typing import Iterator

from ..core import Stats
from .models import Location

# sources
from .ip import ips
from ..google import events as google_events
from ..google.models import Location as GoogleLocation
from ..apple import events as apple_events
from ..apple import Location as AppleLocation


# merges basic location data from multiple sources
# this excludes ip location data which has timezones
# is useful to separate this to allow for easier
# use in my.time.tz.via_location
def basic_locations() -> Iterator[Location]:
    yield from _google_locations()
    yield from _apple_locations()


# location data from all sources, for other uses
def locations() -> Iterator[Location]:
    yield from basic_locations()
    for ip in ips():
        ip_lat, ip_lng = ip.location
        yield Location(lat=ip_lat, lng=ip_lng, dt=ip.at)


# get location data from google exports
def _google_locations() -> Iterator[Location]:
    yield from map(
        lambda gl: Location(lng=gl.lng, lat=gl.lat, dt=gl.at),
        filter(
            lambda g: isinstance(g, GoogleLocation),
            google_events(),
        ),
    )


def _apple_locations() -> Iterator[Location]:
    yield from map(
        lambda al: Location(lng=al.lng, lat=al.lat, dt=al.dt),
        filter(lambda a: isinstance(a, AppleLocation), apple_events()),
    )


def stats() -> Stats:
    from ..core import stat

    return {
        **stat(locations),
    }
