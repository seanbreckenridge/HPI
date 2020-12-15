"""
Parse gpslogger https://github.com/mendhak/gpslogger .gpx (xml) files
"""

from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple, Iterator, Set, Dict

from lxml import etree

from ..core import Stats, Paths, LazyLogger
from ..core.error import Res
from ..core.common import get_files, warn_if_empty, mcachew
from ..core.cachew import cache_dir

# For config, see: https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py
from my.config import gpslogger as user_config


logger = LazyLogger(__name__, level="warning")


@dataclass
class gpslogger(user_config):
    # path[s]/glob to the synced gpx (XML) files
    export_path: Paths


from ..core.cfg import make_config

config = make_config(gpslogger)


class Location(NamedTuple):
    dt: datetime
    lat: float
    lng: float


@mcachew(
    cache_path=cache_dir(),
    depends_on=lambda: list(map(str, get_files(config.export_path))),
    logger=logger,
)
def history() -> Iterator[Res[Location]]:
    files = get_files(config.export_path, glob="*.gpx")

    emitted: Set[datetime] = set()
    for p in files:
        for l in _extract_locations(p):
            if l.dt in emitted:
                continue
            emitted.add(l.dt)
            yield l


def _extract_locations(path: Path) -> Iterator[Res[Location]]:
    try:
        import gpxpy

        with path.open("r") as gf:
            gpx_obj = gpxpy.parse(gf)
            for track in gpx_obj.tracks:
                for segment in track.segments:
                    for point in segment.points:
                        # TODO: use elevation?
                        yield Location(
                            lat=point.latitude,
                            lng=point.longitude,
                            dt=datetime.replace(point.time, tzinfo=timezone.utc),
                        )
    except ImportError:
        logger.warning(
            "Should install 'gpxpy' to parse .gpx files, falling back to basic XML parsing"
        )
        yield from _extract_xml_locations(path)


@warn_if_empty
def _extract_xml_locations(path: Path) -> Iterator[Res[Location]]:
    # the tags are sort of strange here, because they include the
    # input format (URL). cant use findall easily, have to loop through
    # and find substrings of the matching tags
    tr = etree.parse(str(path))
    for el in tr.getroot():  # gpx element
        if el.tag.endswith("trk"):
            for trkseg in el:  # trk
                for trkpt in trkseg:
                    latlon_dict: Dict[str, str] = trkpt.attrib
                    try:
                        assert "lat" in latlon_dict
                        assert "lon" in latlon_dict
                    except AssertionError as ae:
                        return ae
                    for child in trkpt:
                        # believe this is UTC, since gpx times start at 8AM and I'm in PST
                        if child.tag.endswith("time"):
                            yield Location(
                                dt=datetime.astimezone(
                                    datetime.fromisoformat(child.text.rstrip("Z")),
                                    tz=timezone.utc,
                                ),
                                lat=float(latlon_dict["lat"]),
                                lng=float(latlon_dict["lon"]),
                            )
    else:
        return RuntimeError("Could not find 'trk' element in GPX XML")


def stats() -> Stats:
    from ..core import stat

    return {**stat(history)}
