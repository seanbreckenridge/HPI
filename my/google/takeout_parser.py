"""
Parses a Google Takeout https://takeout.google.com/
"""

import os
import string
from pathlib import Path
from typing import Iterator, Union, Any

from .models import HtmlEvent
from .html import read_html

from ..core.error import Res

from ..core.common import LazyLogger  # , mcachew

logger = LazyLogger(__name__)


Event = Union[HtmlEvent]

Results = Iterator[Res[Event]]

CACHEW_PATH = "/tmp/google_html"
if not os.path.exists(CACHEW_PATH):
    os.makedirs(CACHEW_PATH)

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
        "Google Play Store/Installs": None,  # TODO: parse
        "Google Play Store/Library": None,
        "Google Play Store/Purchase History": None,
        "Google Play Store/Subscriptions": None,
        "Google Play Store/Redemption History": None,
        "My Activity/Takeout/MyActivity.html": None,
        "YouTube and YouTube Music/videos": None,
        "Contacts": None,  # TODO: implement, need to parse vcf files
        "Location History/Semantic Location History": None,  # TODO: parse
        "Location History/Location History": None,  # TODO: parse
        "YouTube and YouTube Music/history/search-history": None,  # TODO: parse
        "YouTube and YouTube Music/history/watch-history": None,  # TODO: parse
        "YouTube and YouTube Music/my-comments": None,  # TODO: parse
        "YouTube and YouTube Music/my-live-chat-messages": None,  # TODO: parse
        "YouTube and YouTube Music/playlists/likes.json": None,  # TODO: parse
        "YouTube and YouTube Music/playlists/": None,  # dicts are ordered, so the rest of the stuff is ignored
        "YouTube and YouTube Music/subscriptions": None,  # TODO: parse
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


def _activity_hash(p: Path) -> str:
    full_path: str = str(p)
    alpha_chars = "".join(filter(lambda y: y in string.ascii_letters, full_path))
    return os.path.join(CACHEW_PATH, alpha_chars)


# @mcachew(cache_path=_activity_hash, hashf=lambda p: str(p))
def _parse_html_activity(p: Path) -> Iterator[Res[HtmlEvent]]:
    yield from read_html(p)
