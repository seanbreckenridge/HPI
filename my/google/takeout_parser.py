"""
Parses a Google Takeout https://takeout.google.com/
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Iterator, Union, Any

from .models import HtmlEvent, HtmlComment, LikedVideo, AppInstall, Location
from .html import read_html_activity, read_html_li

from ..core.time import parse_datetime_millis
from ..core.error import Res

from ..core.common import LazyLogger, cachewpath

logger = LazyLogger(__name__, level="warning")


Event = Union[
    HtmlEvent,
    HtmlComment,
    LikedVideo,
    AppInstall,
    Location,
]

Results = Iterator[Res[Event]]


# this currently only parses one takeout
# will probably be extended to merge multiple when I
# actually have multiple google takeouts
def parse_takeout(single_takeout_dir: Path) -> Results:

    # NOTE
    # this is super specific, and it doesnt handle all cases.
    # this is because the google takeout is pretty particular, it depends
    # on what you choose to export. Unhandled files will be yielded as a
    # RuntimeError.
    # to implement one, you have to add a prefix match to the handler_map,
    # and then implement a corresponding function which receives the filename
    # and parses it into whatever events you want.

    # I select:
    # Contacts
    # Google Photos
    # Google Play Store
    # Youtube and Youtube Music (but deseleting music-library-songs, music-uploads and videos options)
    # Location History
    # My Activity
    #
    # Have to manually go to takeout.google.com once per year and select that info, and then it
    # puts the zipped file into google drive at 2 months intervals, 6 times
    #
    # That gets pulled down using https://github.com/odeke-em/drive (https://sean.fish/d/housekeeping?dark)
    # and then unzipped into my ~/data directory (by HPI/scripts/unzip_google_takeout)

    handler_map = {
        "Google Photos": None,  # implemented in photos.py
        "Google Play Store/Devices": None,  # not that interesting
        "archive_browser.html": None,  # description of takeout, not useful
        "Google Play Store/Installs": _parse_app_installs,
        "Google Play Store/Library": None,
        "Google Play Store/Purchase History": None,
        "Google Play Store/Subscriptions": None,
        "Google Play Store/Redemption History": None,
        "My Activity/Takeout/MyActivity.html": None,
        "YouTube and YouTube Music/subscriptions": None,
        "YouTube and YouTube Music/videos": None,
        "Contacts": None,  # TODO: implement, need to parse vcf files
        "Location History/Semantic Location History": None,  # not that much data here. maybe parse it?
        "Location History/Location History": _parse_location_history,
        "YouTube and YouTube Music/history/search-history": _parse_html_activity,
        "YouTube and YouTube Music/history/watch-history": _parse_html_activity,
        "YouTube and YouTube Music/my-comments": _parse_html_chat_li,
        "YouTube and YouTube Music/my-live-chat-messages": _parse_html_chat_li,
        "YouTube and YouTube Music/playlists/likes.json": _parse_likes,
        "YouTube and YouTube Music/playlists/": None,  # dicts are ordered, so the rest of the stuff is ignored
        "My Activity/Ads": _parse_html_activity,
        "My Activity/Android": _parse_html_activity,
        "My Activity/Assistant": _parse_html_activity,
        "My Activity/Books": _parse_html_activity,
        "My Activity/Chrome": _parse_html_activity,
        "My Activity/Drive": _parse_html_activity,
        "My Activity/Developers": _parse_html_activity,
        "My Activity/Discover": _parse_html_activity,
        "My Activity/Gmail": _parse_html_activity,
        "My Activity/Google Analytics": _parse_html_activity,
        "My Activity/Google Apps": _parse_html_activity,
        "My Activity/Google Cloud": _parse_html_activity,
        "My Activity/Google Play Music": _parse_html_activity,
        "My Activity/Google Cloud": _parse_html_activity,
        "My Activity/Google Play Store": _parse_html_activity,
        "My Activity/Help": _parse_html_activity,
        "My Activity/Image Search": _parse_html_activity,
        "My Activity/Maps": _parse_html_activity,
        "My Activity/News": _parse_html_activity,
        "My Activity/Search": _parse_html_activity,
        "My Activity/Shopping": _parse_html_activity,
        "My Activity/Video Search": _parse_html_activity,
        "My Activity/YouTube": _parse_html_activity,
    }
    for f in single_takeout_dir.rglob("*"):
        handler: Any
        for prefix, h in handler_map.items():
            if (
                not str(f).startswith(os.path.join(single_takeout_dir, prefix))
                and f.is_file()
            ):
                continue
            handler = h
            break
        else:
            if f.is_dir():
                continue  # ignore directories
            else:
                e = RuntimeError(f"Unhandled file: {f}")
                logger.debug(str(e))
                yield e
                continue

        if handler is None:
            # explicitly ignored
            continue

        yield from handler(f)


# TODO: enforce UTC? is this UTC?
def _parse_json_date(sdate: str) -> datetime:
    return datetime.strptime(sdate.split(".")[0], "%Y-%m-%dT%H:%M:%S")


def _parse_location_history(p: Path) -> Iterator[Location]:
    ### HMMM, seems that all the locations are right after one another. broken? May just be all the location history that google has on me
    ### see numpy.diff(list(map(lambda yy: y.at, filter(lambda y: isinstance(Location), events()))))
    for japp in json.loads(p.read_text())["locations"]:
        yield Location(
            lng=float(japp["longitudeE7"]) / 1e7,
            lat=float(japp["latitudeE7"]) / 1e7,
            at=parse_datetime_millis(japp["timestampMs"]),
        )


def _parse_app_installs(p: Path) -> Iterator[AppInstall]:
    for japp in json.loads(p.read_text()):
        yield AppInstall(
            title=japp["install"]["doc"]["title"],
            at=_parse_json_date(japp["install"]["firstInstallationTime"]),
        )


def _parse_likes(p: Path) -> Iterator[LikedVideo]:
    for jlike in json.loads(p.read_text()):
        yield LikedVideo(
            title=jlike["snippet"]["title"],
            desc=jlike["snippet"]["description"],
            link="https://youtube.com/watch?v={}".format(
                jlike["contentDetails"]["videoId"]
            ),
            at=_parse_json_date(jlike["snippet"]["publishedAt"]),
        )


def _parse_html_chat_li(p: Path) -> Iterator[Res[HtmlEvent]]:
    yield from read_html_li(p)


CACHEW_PATH = "/tmp/google_html"


@cachewpath(cache_path_base=CACHEW_PATH, logger=logger)
def _parse_html_activity(p: Path) -> Iterator[Res[HtmlEvent]]:
    yield from read_html_activity(p)
