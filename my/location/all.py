"""
Merges location data from multiple sources
"""

from typing import Iterator

from my.core import Stats, LazyLogger
from my.core.common import mcachew
from .models import Location

# sources
from my.location.ip import ips
from my.location.gpslogger import history as gpslogger_history
from my.apple.privacy_export import events as apple_events, Location as AppleLocation

from my.google.takeout.parser import (
    events as google_events,
    _cachew_depends_on as _google_cachew_depends_on,
)
from google_takeout_parser.models import Location as GoogleLocation


logger = LazyLogger(__name__, level="warning")


def exact_locations() -> Iterator[Location]:
    """
    merges basic location data from multiple sources
    this excludes ip location data which has timezones
    is useful to separate this to allow for easier
    use in my.time.tz.via_location
    """
    yield from _google_locations()
    yield from _apple_locations()
    yield from _gpslogger_locations()


# location data from all sources, for other uses
def locations() -> Iterator[Location]:
    yield from exact_locations()
    yield from map(lambda i: i.location, ips())


# get location data from google exports
@mcachew(
    depends_on=_google_cachew_depends_on,
    logger=logger,
)
def _google_locations() -> Iterator[Location]:
    for g in google_events():
        if isinstance(g, GoogleLocation) and not isinstance(g, Exception):
            yield Location(lng=g.lng, lat=g.lat, dt=g.dt, accuracy=True)


# cachew is handled in apple_events, I think this is fast enough
def _apple_locations() -> Iterator[Location]:
    for a in apple_events():
        if isinstance(a, AppleLocation) and not isinstance(a, Exception):
            yield Location(lng=a.lng, lat=a.lat, dt=a.dt, accuracy=True)


def _gpslogger_locations() -> Iterator[Location]:
    for gl in gpslogger_history():
        yield Location(
            lng=gl.lng,
            lat=gl.lat,
            dt=gl.dt,
            accuracy=True,
        )


def stats() -> Stats:
    from my.core import stat

    return {
        **stat(locations),
    }
