"""
Parses the facebook GPDR Export
"""

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
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
from typing import Iterable, Dict, Any, NamedTuple, Union, Optional, List

from .core.error import Res
from .core import get_files

from .core.common import LazyLogger

logger = LazyLogger(__name__)

Json = Dict[str, Any]


class Contact(NamedTuple):
    name: str
    phone_number: str
    created: datetime
    updated: datetime


class Action(NamedTuple):
    description: str
    at: datetime
    metadata: Json = {}


# (logs/account activity)
class AdminAction(NamedTuple):
    description: str
    at: datetime
    ip: str
    user_agent: str
    metadata: Json = {}


class Search(NamedTuple):
    query: str
    at: datetime


class Post(NamedTuple):
    content: str
    at: datetime
    action: Optional[str]


class Comment(NamedTuple):
    action: str
    at: datetime
    content: str
    metadata: Optional[str]


class AcceptedEvent(NamedTuple):
    name: str
    starts_at: datetime
    ends_at: datetime


class Friend(NamedTuple):
    name: str
    at: datetime
    added: bool  # whether this was when I added a friend or removed one


# i.e. a PM
class Message(NamedTuple):
    author: str
    at: datetime
    content: str
    metadata: Optional[str] = None


# a chain of messages back and forth, with one or more people
class Conversation(NamedTuple):
    title: str
    participants: List[str]
    messages: List[Message]


Event = Union[
    Contact,
    Conversation,
    Friend,
    AcceptedEvent,
    Action,
    Post,
    Comment,
    Search,
    AdminAction,
    Contact,
]


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
        "likes_and_reactions/pages": _parse_page_likes,
        "likes_and_reactions/posts_and_comments": _parse_reactions,
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
        "posts/your_posts": _parse_posts,
        "search_history": _parse_search_history,
        "profile_information/profile_update_history": _parse_posts,
        "messages/stickers_used": None,  # no one needs stickers o_o
        "messages/": _parse_conversation,
        "security_and_login_information/account_activity": _parse_account_activity,
        "security_and_login_information/authorized_logins": _parse_authorized_logins,
        "security_and_login_information/administrative_records": _parse_admin_records,
        "security_and_login_information/where_you": None,
        "security_and_login_information/used_ip_addresses": None,
        "security_and_login_information/account_status_changes": None,
        "security_and_login_information/logins_and_logouts": None,
        "security_and_login_information/login_protection": None,
        "security_and_login_information/datr_cookie": None,
        "posts/other_people's_posts_to_your_timeline": None,  # maybe implement this? OtherComment NamedTuple? Comment should just be mine
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
            # explicitly ignored
            continue

        if f.is_dir():
            # rglob("*") matches directories, as well as any subredirectories/json files in those
            # this is here exclusively for the messages dir, which has a larger structure
            # json files from inside the dirs are still picked up by rglob
            continue

        if f.suffix != ".json":
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


def _parse_installed_apps(d: Dict) -> Iterable[Action]:
    for app in d["installed_apps"]:
        yield Action(
            description="{} was installed".format(app["name"]),
            at=fepoch(app["added_timestamp"]),
        )


def _parse_app_posts(d: Dict) -> Iterable[Action]:
    for post in d["app_posts"]:
        yield Action(description=post["title"], at=fepoch(post["timestamp"]))


def _parse_group_comments(d: Dict) -> Iterable[Comment]:
    for comment in d["comments"]:
        yield Comment(
            content=comment["data"][0]["comment"]["comment"],
            action=comment["title"],
            at=fepoch(comment["timestamp"]),
            metadata=comment["data"][0]["comment"]["group"],
        )


def _parse_joined_events(d: Dict) -> Iterable[AcceptedEvent]:
    for event in d["event_responses"]["events_joined"]:
        yield AcceptedEvent(
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


def _parse_page_likes(d: Dict) -> Iterable[Action]:
    for page in d["page_likes"]:
        yield Action(
            description="Liked Page {}".format(page["name"]),
            at=fepoch(page["timestamp"]),
        )


def _parse_reactions(d: Dict) -> Iterable[Action]:
    for react in d["reactions"]:
        yield Action(description=react["title"], at=fepoch(react["timestamp"]))


def _parse_search_history(d: Dict) -> Iterable[Search]:
    for search in d["searches"]:
        assert len(search["data"]) == 1
        yield Search(query=search["data"][0]["text"], at=fepoch(search["timestamp"]))


def _parse_conversation(
    d: Dict,
) -> Iterable[Res[Conversation]]:  # will only return 1 convo
    participants: List[str] = [p["name"] for p in d["participants"]]
    messages = list(_parse_messages_in_conversation(d["messages"]))
    # propogate up exception if one exists
    try:
        yield next(filter(lambda m: isinstance(m, Exception), messages))
    except StopIteration:  # there was no error found out
        yield Conversation(
            participants=participants,
            title=d["title"],
            messages=messages,
        )


def _parse_messages_in_conversation(messages: List[Dict]) -> Iterable[Res[Message]]:
    for m in messages:
        timestamp = fepoch(m["timestamp_ms"] / 1000)
        author = m["sender_name"]
        if m["type"] == "Unsubscribe":
            continue
        elif m["type"] in ["Generic", "Share"]:
            # eh, I dont care that much about these in context, can do anaylsis on my/photos.py on its own
            if any([k in m for k in ["photos", "sticker"]]):
                continue
            elif "content" in m:
                yield Message(
                    at=timestamp,
                    author=author,
                    content=m["content"],
                    metadata=m.get("share"),
                )
            # if this just actually doesnt have a field with content for some reason, ignore it
            elif set(m.keys()).issubset(set(["sender_name", "timestamp_ms", "type"])):
                continue
            else:
                yield RuntimeError(
                    "Not sure how to parse message without 'photos' or 'content': {}".format(
                        m
                    )
                )
        else:
            yield RuntimeError("Not sure how to parse message for type: {}".format(m))


# yikes. this is pretty much whenever I posted *anything*, or a third party app communicated
# back to facebook that I listened to something/played a game, so it has like 5000 events
#
# not sure if I hit all the types, but this yields RuntimeErrors if it cant parse something,
# so just check hpi doctor to make sure its all gooood
# or
# list(filter(lambda e: isinstance(e, Exception), events())),
# throw a 'import pdb; pdb.set_trace()' at where its throwing the error
# and add a new case for a new type of post
def _parse_posts(d: Dict) -> Iterable[Res[Union[Post, Action]]]:
    all_posts = d
    # handle both profile updates and posts
    if isinstance(all_posts, dict) and "profile_updates" in all_posts:
        all_posts = all_posts["profile_updates"]
    for post in all_posts:
        if "attachments" in post:
            att = post["attachments"]
            # e.g. photo with a description
            # make sure the structure looks like a media post
            # traverse into the image metadata post to see if we can find a description
            if len(att) >= 1 and "data" in att[0] and len(att[0]["data"]) >= 1:
                # make sure each data item has only one item of media
                if all([len(attach["data"]) == 1 for attach in att]):
                    att_data = [attach["data"][0] for attach in att]
                    # switch, over posts that have descriptions (e.g. me describing what the photo is), and posts that dont
                    for dat in att_data:
                        if "media" in dat:
                            mdat = dat["media"]
                            # image where I described something
                            if "description" in mdat:
                                yield Action(
                                    description=mdat["description"],
                                    at=fepoch(post["timestamp"]),
                                    metadata=mdat,
                                )
                            # image when I just posted to a album
                            elif "title" in mdat:
                                yield Action(
                                    description="Posted to Album {}".format(
                                        mdat["title"]
                                    ),
                                    at=fepoch(post["timestamp"]),
                                    metadata=mdat,
                                )
                            else:
                                yield RuntimeError(
                                    "No known way to parse image post {}".format(post)
                                )
                        elif "place" in dat:
                            # check-in into place
                            if "name" in dat["place"]:
                                yield Action(
                                    description="Visited {}".format(
                                        dat["place"]["name"]
                                    ),
                                    at=fepoch(post["timestamp"]),
                                    metadata=dat,
                                )
                            else:
                                yield RuntimeError(
                                    "No known way to parse location post {}".format(
                                        post
                                    )
                                )
                        elif "life_event" in dat:
                            # started high school etc.
                            ddat = dat["life_event"]
                            yield Action(
                                description=ddat["title"],
                                at=fepoch(post["timestamp"]),
                                metadata=ddat,
                            )
                        # third party app event (e.g. Listened to Spotify Song)
                        elif "title" in post:
                            if "external_context" in dat:
                                if "title" in post:
                                    yield Action(
                                        description=post["title"],
                                        at=fepoch(post["timestamp"]),
                                        metadata=dat,
                                    )
                            # seems like bad data handling on facebooks part.
                            # these are still events,
                            # but it doesnt have an external context,
                            # its like a stringified version of the data
                            elif "text" in dat:
                                yield Action(
                                    description=post["title"],
                                    at=fepoch(post["timestamp"]),
                                    metadata=dat,
                                )
                            else:
                                yield RuntimeError(
                                    "No known way to parse attachment post with title {}".format(
                                        post
                                    )
                                )
                        else:  # unknown data type
                            yield RuntimeError(
                                "No known way to parse data type with attachment {}".format(
                                    post
                                )
                            )
                else:  # unknown structure
                    yield RuntimeError(
                        "No known way to parse data from post {}".format(post)
                    )
            else:
                yield RuntimeError(
                    "No known way to parse attachment post {}".format(post)
                )
        elif "data" in post and len(post["data"]) == 1:
            dat = post["data"][0]
            # basic post I wrote on my timeline
            if "post" in dat and isinstance(dat["post"], str) and "title" in post:
                yield Post(
                    content=dat["post"],
                    at=fepoch(post["timestamp"]),
                    action=post["title"],
                )
            elif "profile_update" in dat:
                yield Action(
                    description="Updated Profile",
                    at=fepoch(post["timestamp"]),
                    metadata=dat["profile_update"],
                )
            else:
                yield RuntimeError("No known way to parse basic post {}".format(post))
        # post without any actual content (e.g. {'timestamp': 1334515711, 'title': 'Sean Breckenridge posted in club'})
        # treat this as an action since I have no content here
        elif set(("timestamp", "title")) == set(post.keys()):
            yield Action(description=post["title"], at=fepoch(post["timestamp"]))
        else:
            yield RuntimeError("No known way to parse post {}".format(post))


def _parse_account_activity(d: Dict) -> Iterable[AdminAction]:
    for ac in d["account_activity"]:
        yield AdminAction(
            description=ac["action"],
            at=fepoch(ac["timestamp"]),
            ip=ac["ip_address"],
            user_agent=ac["user_agent"],
        )


def _parse_authorized_logins(d: Dict) -> Iterable[AdminAction]:
    for ac in d["recognized_devices"]:
        metadata = {}
        if "updated_timestamp" in ac:
            metadata["updated_at"] = fepoch(ac["updated_timestamp"])
        yield AdminAction(
            description="Known Device: {}".format(ac["name"]),
            at=fepoch(ac["created_timestamp"]),
            ip=ac["ip_address"],
            user_agent=ac["user_agent"],
            metadata=metadata,
        )


def _parse_admin_records(d: Dict) -> Iterable[AdminAction]:
    for rec in d["admin_records"]:
        s = rec["session"]
        yield AdminAction(
            description=rec["event"],
            at=fepoch(s["created_timestamp"]),
            ip=s["ip_address"],
            user_agent=s["user_agent"],
        )


def fepoch(epoch_time: int) -> datetime:
    return datetime.fromtimestamp(epoch_time, tz=timezone.utc)
