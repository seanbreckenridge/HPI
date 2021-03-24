from more_itertools import ilen

from my.google import events, raw_events
from my.google.models import (
    Location,
    AppInstall,
    LikedVideo,
    HtmlComment,
    HtmlEvent,
    HtmlCommentLinks,
    HtmlEventLinks,
)


def test_google_types():
    all_ev = list(events())
    assert len(all_ev) > 100
    all_types = set([Location, AppInstall, LikedVideo, HtmlComment, HtmlEvent])
    assert all_types == set(map(type, all_ev))
    # make sure we parsed everything without errors
    assert ilen(filter(lambda e: isinstance(e, Exception), all_ev)) == 0

    raw_ev = list(raw_events())
    raw_types = set(
        [Location, AppInstall, LikedVideo, HtmlCommentLinks, HtmlEventLinks]
    )
    assert raw_types == set(map(type, raw_ev))
