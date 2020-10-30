"""
Merges location data from multiple sources
"""

from typing import Iterator

from ..core import Stats, LazyLogger
from ..core.common import mcachew
from ..core.cachew import cache_dir
from .models import Location

# sources
from .ip import ips
from .gpslogger import history as gpslogger_history
from ..google import events as google_events, get_last_takeout
from ..google.models import Location as GoogleLocation
from ..apple import events as apple_events
from ..apple import Location as AppleLocation


logger = LazyLogger(__name__, level="warning")

# merges basic location data from multiple sources
# this excludes ip location data which has timezones
# is useful to separate this to allow for easier
# use in my.time.tz.via_location
def exact_locations() -> Iterator[Location]:
    yield from _google_locations()
    yield from _apple_locations()
    yield from _gpslogger_locations()


# location data from all sources, for other uses
def locations() -> Iterator[Location]:
    yield from exact_locations()
    yield from map(lambda i: i.location, ips())


# get location data from google exports
@mcachew(
    cache_path=cache_dir(),
    depends_on=lambda: str(get_last_takeout()),
    logger=logger,
)
def _google_locations() -> Iterator[Location]:
    yield from map(
        lambda gl: Location(lng=gl.lng, lat=gl.lat, dt=gl.at, accuracy=True),
        filter(
            lambda g: isinstance(g, GoogleLocation),
            google_events(),
        ),
    )


# cachew is handled in apple_events, I think this is fast enough
def _apple_locations() -> Iterator[Location]:
    yield from map(
        lambda al: Location(lng=al.lng, lat=al.lat, dt=al.dt, accuracy=True),
        filter(lambda a: isinstance(a, AppleLocation), apple_events()),
    )


def _gpslogger_locations() -> Iterator[Location]:
    for gl in gpslogger_history():
        if isinstance(gl, Exception):
            logger.exception(gl)
        else:
            yield Location(
                lng=gl.lng,
                lat=gl.lat,
                dt=gl.dt,
                accuracy=True,
            )


def stats() -> Stats:
    from ..core import stat

    return {
        **stat(locations),
    }
