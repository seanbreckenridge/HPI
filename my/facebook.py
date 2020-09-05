"""
Parses the facebook GPDR Export
"""

# TODO later, use a separate user config? (github_gdpr)
from my.config import facebook as user_config

from dataclasses import dataclass
from .core import PathIsh


@dataclass
class facebook(user_config):
    gdpr_dir: PathIsh  # path to unpacked GDPR archive


from .core.cfg import make_config

config = make_config(facebook)

import os
import json
from datetime import datetime, timezone
from pathlib import Path
from itertools import chain
from typing import Iterable, Dict, Any, NamedTuple, Union, Optional

from .core.error import Res
from .core import get_files

from .core.common import LazyLogger

logger = LazyLogger(__name__)


class Contact(NamedTuple):
    name: str
    phone_number: str
    created: datetime
    updated: datetime


class AppInstall(NamedTuple):
    name: str
    added: datetime


class Action(NamedTuple):
    description: str
    at: datetime


class ThirdPartyAction(Action):
    pass


class Post(NamedTuple):
    content: str
    at: datetime
    action: Optional[str]


class Comment(NamedTuple):
    action: str
    at: datetime
    content: str
    metadata: Optional[str]


class JoinedEvent(NamedTuple):
    name: str
    starts_at: datetime
    ends_at: datetime


class Friend(NamedTuple):
    name: str
    at: datetime
    added: bool  # whether this was when I added a friend or removed one


class PageLike(NamedTuple):
    name: str
    at: datetime


Event = Union[Contact, AppInstall]


def events() -> Iterable[Res[Event]]:
    # get files 2 levels deep into the export
    gdpr_dir = str(Path(config.gdpr_dir).expanduser().absolute())  # expand path
    files = chain(*map(lambda f: f.rglob("*"), get_files(config.gdpr_dir)))
    handler_map = {
        "about_you/face_recog": None,
        "about_you/friend_peer": None,
        "about_you/your_address_books": _parse_address_book,
        "ads": None,
        "apps_and_websites/apps_and_websites": _parse_installed_apps,
        "apps_and_websites/posts_from_apps_and_websites": _parse_app_posts,
        "comments/comments": _parse_group_comments,
        "events/event_invitations": None,  # just parse the ones I accepted
        "events/your_event_responses": _parse_joined_events,
        "following_and": None,  # I have no data here
        "friends/friends": _parse_friends,
        "friends/received_friend_requests": None,  # Not interested
        "friends/rejected_friend": None,  # Not interested
        "friends/sent_friend": None,  # Not interested
        "friends/removed_": _parse_deleted_friends,
        "groups/your_group_membership": _parse_group_activity,
        "groups/your_posts_and_comments": _parse_group_posts,
        "likes_and_reactions/pages.json": _parse_page_likes,
        "likes_and_reactions/posts_and_comments": _parse_reactions,
        "messages/stickers_used": None,
        "location": None,  # No data
        "marketplace": None,
        "other_activity": None,
        "pages": None,
        "payment_history": None,
        "photos_and_videos": None,  # pull these out in my/photos.py
        "profile_information/profile_information.json": None,
        "saved_items": None,
        "stories": None,
        "your_places": None,
        "security_and_login_information/": None,  # implement
        "messages/": None,  # implement
        "profile_information/profile_update_history": None,  # implement
        "search_history": None,  # implement
        "posts/": None,  # implement
    }
    for f in files:
        handler: Any
        for prefix, h in handler_map.items():
            if not str(f).startswith(os.path.join(gdpr_dir, prefix)):
                continue
            handler = h
            break
        else:
            e = RuntimeError(f"Unhandled file: {f}")
            logger.debug(str(e))
            yield e
            continue

        if handler is None:
            # ignored
            continue

        j = json.loads(f.read_text())
        yield from handler(j)


def stats():
    from .core import stat

    return {
        **stat(events),
    }


def _parse_address_book(d: Dict) -> Iterable[Contact]:
    # remove top-level address book name
    for addr_book_top in d.values():
        for addr_book_list in addr_book_top.values():
            for contact in addr_book_list:
                yield Contact(
                    name=contact["name"],
                    phone_number=contact["details"][0]["contact_point"],
                    created=fepoch(contact["created_timestamp"]),
                    updated=fepoch(contact["updated_timestamp"]),
                )


def _parse_installed_apps(d: Dict) -> Iterable[AppInstall]:
    for app in d["installed_apps"]:
        yield AppInstall(
            name=app["name"],
            added=fepoch(app["added_timestamp"]),
        )


def _parse_app_posts(d: Dict) -> Iterable[ThirdPartyAction]:
    for post in d["app_posts"]:
        yield ThirdPartyAction(description=post["title"], at=fepoch(post["timestamp"]))


def _parse_group_comments(d: Dict) -> Iterable[Comment]:
    for comment in d["comments"]:
        yield Comment(
            content=comment["data"][0]["comment"]["comment"],
            action=comment["title"],
            at=fepoch(comment["timestamp"]),
            metadata=comment["data"][0]["comment"]["group"],
        )


def _parse_joined_events(d: Dict) -> Iterable[JoinedEvent]:
    for event in d["event_responses"]["events_joined"]:
        yield JoinedEvent(
            name=event["name"],
            starts_at=fepoch(event["start_timestamp"]),
            ends_at=fepoch(event["end_timestamp"]),
        )


def _parse_friends(d: Dict) -> Iterable[Friend]:
    for friend in d["friends"]:
        yield Friend(name=friend["name"], at=fepoch(friend["timestamp"]), added=True)


def _parse_deleted_friends(d: Dict) -> Iterable[Friend]:
    for friend in d["deleted_friends"]:
        yield Friend(name=friend["name"], at=fepoch(friend["timestamp"]), added=False)


def _parse_group_activity(d: Dict) -> Iterable[Action]:
    for gr in d["groups_joined"]:
        yield Action(
            description=gr["title"],
            at=fepoch(gr["timestamp"]),
        )


def _parse_group_posts(d: Dict) -> Iterable[Union[Comment, Post]]:
    for log_data_list in d.values():
        for comm_list in log_data_list.values():
            for comm in comm_list:
                data_keys = comm["data"][0].keys()
                if "comment" in data_keys:
                    yield Comment(
                        content=comm["data"][0]["comment"]["comment"],
                        action=comm["title"],
                        at=fepoch(comm["timestamp"]),
                        metadata=comm["data"][0]["comment"]["group"],
                    )
                else:
                    yield Post(
                        content=comm["data"][0]["post"],
                        action=comm["title"],
                        at=fepoch(comm["timestamp"]),
                    )


def _parse_page_likes(d: Dict) -> Iterable[PageLike]:
    for page in d["page_likes"]:
        yield PageLike(name=page["name"], at=fepoch(page["timestamp"]))


def _parse_reactions(d: Dict) -> Iterable[Action]:
    for react in d["reactions"]:
        yield Action(description=react["title"], at=fepoch(react["timestamp"]))


def fepoch(epoch_time: int) -> datetime:
    return datetime.fromtimestamp(epoch_time, tz=timezone.utc)
