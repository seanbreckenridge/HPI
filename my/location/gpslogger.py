"""
Parse gpslogger https://github.com/mendhak/gpslogger .gpx (xml) files
"""

REQUIRES = ["gpxpy"]

# For config, see: https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py
from my.config import gpslogger as user_config  # type: ignore[attr-defined]
from my.core import Paths, dataclass


@dataclass
class config(user_config):
    # path[s]/glob to the synced gpx (XML) files
    export_path: Paths


from itertools import chain
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple, Iterator, Sequence, List

import gpxpy  # type: ignore[import]
from more_itertools import unique_everseen

from my.core import Stats, LazyLogger
from my.core.common import get_files, mcachew
from my.utils.input_source import InputSource


logger = LazyLogger(__name__, level="warning")


class Location(NamedTuple):
    dt: datetime
    lat: float
    lng: float


Results = Iterator[Location]


def inputs() -> Sequence[Path]:
    return get_files(config.export_path, glob="*.gpx")


def _cachew_depends_on(from_paths: InputSource) -> List[float]:
    return [p.stat().st_mtime for p in sorted(from_paths())]


@mcachew(depends_on=_cachew_depends_on, logger=logger)
def history(from_paths: InputSource = inputs) -> Results:
    yield from unique_everseen(
        chain(*map(_extract_locations, from_paths())), key=lambda loc: loc.dt
    )


def _extract_locations(path: Path) -> Iterator[Location]:
    with path.open("r") as gf:
        gpx_obj = gpxpy.parse(gf)
        for track in gpx_obj.tracks:
            for segment in track.segments:
                for point in segment.points:
                    if point.time is None:
                        continue
                    # TODO: use elevation?
                    yield Location(
                        lat=point.latitude,
                        lng=point.longitude,
                        dt=datetime.replace(point.time, tzinfo=timezone.utc),
                    )


def stats() -> Stats:
    from my.core import stat

    return {**stat(history)}
