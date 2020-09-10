"""
Parses a Google Takeout https://takeout.google.com/
"""

import os
from pathlib import Path
from typing import Iterator, NamedTuple, Union, Any

from ..core.error import Res

from ..core.common import LazyLogger

logger = LazyLogger(__name__)


class AppInstall(NamedTuple):
    pass


Event = Union[
    AppInstall,
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
    # and then implement a corresponding function which recieves the filename
    # and parses it into whatever events you want.
    handler_map = {
        "Calendar": None,  # will use google API to get events instead
        "Chrome": None,
        "Google Photos": None,  # implemented in photos.py
        "Google Play Store/Devices": None,  # not that interesting
        "archive_browser.html": None,  # description of takeout, not useful
        "Google Play Store/Installs": _parse_google_play_installs,  # TODO: parse
        "Google Play Store/Library": None,
        "Google Play Store/Purchase History": None,
        "YouTube and YouTube Music/videos": None,
        "Contacts": None,  # TODO: implement, need to parse vcf files
        "Location History/Semantic Location History": None,  # TODO: parse
        "Location History/Location History": None,  # TODO: parse
        "YouTube and YouTube Music/history/search-history": None,  # TODO: parse
        "YouTube and YouTube Music/history/watch-history": None,  # TODO: parse
        "YouTube and YouTube Music/my-comments": None,  # TODO: parse
        "YouTube and YouTube Music/my-live-chat-messages": None,  # TODO: parse
        "YouTube and YouTube Music/playlists/likes.json": _parse_likes,  # TODO: parse
        "YouTube and YouTube Music/playlists/": None,  # dicts are ordered, so the rest of the stuff is ignored
        "YouTube and YouTube Music/subscriptions": _parse_subscriptions,  # TODO: parse
        "My Activity/Ads": _parse_ads,  # TODO: parse
        "My Activity/Android": None,  # TODO: parse
        "My Activity/Assistant": None,  # TODO: parse
        "My Activity/Books": None,  # TODO: parse
        "My Activity/Chrome": None,  # TODO: parse
        "My Activity/Drive": None,
        "My Activity/Developers": None,  # TODO: parse
        "My Activity/Discover": None,  # TODO: parse
        "My Activity/Discover": None,  # TODO: parse
        "My Activity/Gmail": None,  # TODO: parse
        "My Activity/Google Analytics": None,  # TODO: parse
        "My Activity/Google Apps": None,
        "My Activity/Google Cloud": None,  # TODO: parse
        "My Activity/Google Play Music": None,
        "My Activity/Google Cloud": None,  # TODO: parse
        "My Activity/Google Play Store": None,  # TODO: parse
        "My Activity/Help": None,  # TODO: parse
        "My Activity/Image Search": None,  # TODO: parse
        "My Activity/Maps": None,  # TODO: parse
        "My Activity/News": None,  # TODO: parse
        "My Activity/Search": None,  # TODO: parse
        "My Activity/Shopping": None,
        "My Activity/Video Search": None,  # TODO: parse
        "My Activity/YouTube": None,  # TODO: parse
    }
    for f in single_takeout_dir.rglob("*"):
        handler: Any
        for prefix, h in handler_map.items():
            if not str(f).startswith(os.path.join(single_takeout_dir, prefix)):
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


def _parse_google_play_installs(f: Path) -> Iterator[AppInstall]:
    yield None


def _parse_likes(f: Path):
    yield None


def _parse_subscriptions(f: Path):
    yield None


def _parse_ads(f: Path):
    yield None
