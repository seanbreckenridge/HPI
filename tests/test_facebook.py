from more_itertools import ilen

from my.facebook import *


def test_facebook_types():
    all_ev = list(events())
    assert len(all_ev) > 100
    all_types = set(
        [
            Contact,
            Action,
            AdminAction,
            UploadedPhoto,
            Search,
            Post,
            Comment,
            AcceptedEvent,
            Friend,
            Conversation,
        ]
    )
    assert all_types == set(map(type, all_ev))
    # make sure we parsed everything without errors
    assert ilen(filter(lambda e: isinstance(e, Exception), all_ev)) == 0
