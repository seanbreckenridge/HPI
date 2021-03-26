"""
Parses a Google Takeout https://takeout.google.com/
"""

import os
import json
import string
from pathlib import Path
from datetime import datetime, timezone
from typing import Iterator, Union, Any

from my.core.error import Res
from my.core.common import LazyLogger, mcachew
from my.core.cachew import cache_dir

from .models import (
    HtmlEventLinks,
    HtmlCommentLinks,
    LikedVideo,
    AppInstall,
    Location,
    HtmlEvent,
    HtmlComment,
)
from .html import read_html_activity, read_html_li
from .json import read_youtube_json_history
from ..utils.time import parse_datetime_millis


def simplify_path(p: Path) -> str:
    """
    >>> Path("/home/sometihng/else.txt")
    'homesomethingelsetxt'
    """
    full_path: Path = p.expanduser().absolute()
    return "".join(
        filter(lambda y: y in string.ascii_letters + string.digits, str(full_path))
    )


logger = LazyLogger(__name__, level="warning")


RawEvent = Union[
    HtmlEventLinks,
    HtmlCommentLinks,
    LikedVideo,
    AppInstall,
    Location,
]


RawResults = Iterator[Res[RawEvent]]

Event = Union[HtmlEvent, HtmlComment, LikedVideo, AppInstall, Location]

Results = Iterator[Res[Event]]


# this currently only parses one takeout
# will probably be extended to merge multiple when I
# actually have multiple google takeouts
def parse_takeout(single_takeout_dir: Path) -> RawResults:

    # NOTE
    # this is super specific, and it doesnt handle all cases.
    # this is because the google takeout is pretty particular, it depends
    # on what you choose to export. Unhandled files will be yielded as a
    # RuntimeError.
    # to implement one, you have to add a prefix match to the handler_map,
    # and then implement a corresponding function which receives the filename
    # and parses it into whatever events you want.

    # I select:
    # Google Play Store
    # Location History
    # My Activity
    # Youtube and Youtube Music
    #   - go to options and select JSON instead of HTML
    #   - deselect music-library-songs, music-uploads and videos options)
    #
    # Have to manually go to takeout.google.com once per year and select that info, and then it
    # puts the zipped file into google drive at 2 months intervals, 6 times
    #
    # That gets pulled down using https://github.com/odeke-em/drive (https://sean.fish/d/housekeeping?dark)
    # and then unzipped into my ~/data directory (by HPI/scripts/unzip_google_takeout)

    handler_map = {
        "Google Photos": None,  # some of my old takeouts have this, dont use it anymore
        "Google Play Store/Devices": None,  # not that interesting
        "archive_browser.html": None,  # description of takeout, not useful
        "Google Play Store/Installs": _parse_app_installs,
        "Google Play Store/Library": None,
        "Google Play Store/Purchase History": None,
        "Google Play Store/Subscriptions": None,
        "Google Play Store/Redemption History": None,
        "Google Play Store/Promotion History": None,
        "My Activity/Takeout/MyActivity.html": None,
        "YouTube and YouTube Music/subscriptions": None,
        "YouTube and YouTube Music/videos": None,
        "Location History/Semantic Location History": None,  # not that much data here. maybe parse it?
        "Location History/Location History": _parse_location_history,
        "YouTube and YouTube Music/history/search-history.html": _parse_html_activity,
        "YouTube and YouTube Music/history/watch-history.html": _parse_html_activity,
        "YouTube and YouTube Music/history/search-history.json": _parse_json_youtube_history,
        "YouTube and YouTube Music/history/watch-history.json": _parse_json_youtube_history,
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
        "My Activity/Google Translate": _parse_html_activity,
        "My Activity/Podcasts": _parse_html_activity,
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


# in UTC
def _parse_json_date(sdate: str) -> datetime:
    return datetime.replace(
        datetime.fromisoformat(sdate.split(".")[0]), tzinfo=timezone.utc
    )
    # return datetime.replace(datetime.strptime(sdate.split(".")[0], "%Y-%m-%dT%H:%M:%S"), tzinfo=timezone.utc)


def _parse_location_history(p: Path) -> Iterator[Location]:
    ### HMMM, seems that all the locations are right after one another. broken? May just be all the location history that google has on me
    ### see numpy.diff(list(map(lambda yy: y.at, filter(lambda y: isinstance(Location), events()))))
    for japp in json.loads(p.read_text())["locations"]:
        yield Location(
            lng=float(japp["longitudeE7"]) / 1e7,
            lat=float(japp["latitudeE7"]) / 1e7,
            dt=parse_datetime_millis(japp["timestampMs"]),
        )


def _parse_app_installs(p: Path) -> Iterator[AppInstall]:
    for japp in json.loads(p.read_text()):
        yield AppInstall(
            title=japp["install"]["doc"]["title"],
            dt=_parse_json_date(japp["install"]["firstInstallationTime"]),
        )


def _parse_likes(p: Path) -> Iterator[LikedVideo]:
    for jlike in json.loads(p.read_text()):
        yield LikedVideo(
            title=jlike["snippet"]["title"],
            desc=jlike["snippet"]["description"],
            link="https://youtube.com/watch?v={}".format(
                jlike["contentDetails"]["videoId"]
            ),
            dt=_parse_json_date(jlike["snippet"]["publishedAt"]),
        )


def _parse_html_chat_li(p: Path) -> Iterator[Res[HtmlCommentLinks]]:
    yield from read_html_li(p)


@mcachew(
    cache_path=lambda p: str(cache_dir() / "_parse_html_activity" / simplify_path(p)),
    force_file=True,
    logger=logger,
)
def _parse_html_activity(p: Path) -> Iterator[Res[HtmlEventLinks]]:
    yield from read_html_activity(p)


@mcachew(
    cache_path=lambda p: str(
        cache_dir() / "_parse_json_youtube_history" / simplify_path(p)
    ),
    force_file=True,
    logger=logger,
)
def _parse_json_youtube_history(p: Path) -> Iterator[HtmlEventLinks]:
    yield from read_youtube_json_history(p)
