from typing import Iterator

from my.core.source import import_source
from my.location.common import Location  # type: ignore[attr-defined]


@import_source(module_name="my.apple.privacy_export")
def locations() -> Iterator[Location]:
    from my.apple.privacy_export import events, Location as AppleLocation

    for a in events():
        if isinstance(a, AppleLocation) and not isinstance(a, Exception):
            yield Location(lon=a.lng, lat=a.lat, dt=a.dt, accuracy=50, elevation=None)
