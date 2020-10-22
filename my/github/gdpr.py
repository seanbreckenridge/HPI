"""
Github data (uses [[https://github.com/settings/admin][official GDPR export]])
"""

import json
from typing import Iterator, Dict, Any

from ..core.error import Res
from ..core import get_files

from .common import Event, parse_dt

# TODO later, use a separate user config? (github_gdpr)
from my.config import github as user_config

from dataclasses import dataclass
from ..core import PathIsh, Stats


@dataclass
class github(user_config):
    gdpr_dir: PathIsh  # path to unpacked GDPR archive


###


from ..core.cfg import make_config

config = make_config(github)


def events() -> Iterator[Res[Event]]:
    # TODO FIXME allow using archive here?
    files = get_files(config.gdpr_dir, glob="*.json")
    handler_map = {
        "schema": None,
        "issue_events_": None,  # eh, doesn't seem to have any useful bodies
        "attachments_": None,  # not sure if useful
        "users": None,  # just contains random users
        "projects": None,  # eh, kan-bans arent that useful
        "repositories_": _parse_repository,
        "issue_comments_": _parse_issue_comment,
        "issues_": _parse_issue,
        "pull_requests_": _parse_pull_request,
        "releases_": _parse_release,
        "commit_comments": _parse_commit_comment,
    }
    for f in files:
        handler: Any
        for prefix, h in handler_map.items():
            if not f.name.startswith(prefix):
                continue
            handler = h
            break
        else:
            yield RuntimeError(f"Unhandled file: {f}")
            continue

        if handler is None:
            # ignored
            continue

        j = json.loads(f.read_text())
        for r in j:
            try:
                yield handler(r)
            except Exception as e:
                yield e


def stats() -> Stats:
    from ..core import stat

    return {
        **stat(events),
    }


# TODO typing.TypedDict could be handy here..
def _parse_common(d: Dict) -> Dict:
    url = d["url"]
    body = d.get("body")
    return {
        "dt": parse_dt(d["created_at"]),
        "link": url,
        "body": body,
    }


def _parse_repository(d: Dict) -> Event:
    pref = "https://github.com/"
    url = d["url"]
    assert url.startswith(pref)
    name = url[len(pref) :]
    return Event(  # type: ignore[misc]
        **_parse_common(d),
        summary="created " + name,
        eid="created_" + name,  # TODO ??
    )


def _parse_issue_comment(d: Dict) -> Event:
    url = d["url"]
    is_bot = "[bot]" in d["user"]
    return Event(  # type: ignore[misc]
        **_parse_common(d),
        summary=f"commented on issue {url}",
        eid="issue_comment_" + url,
        is_bot=is_bot,
    )


def _parse_issue(d: Dict) -> Event:
    url = d["url"]
    title = d["title"]
    is_bot = "[bot]" in d["user"]
    return Event(  # type: ignore[misc]
        **_parse_common(d),
        summary=f"opened issue {title}",
        eid="issue_comment_" + url,
        is_bot=is_bot,
    )


def _parse_pull_request(d: Dict) -> Event:
    url = d["url"]
    title = d["title"]
    is_bot = "[bot]" in d["user"]
    return Event(  # type: ignore[misc]
        **_parse_common(d),
        # TODO distinguish incoming/outgoing?
        # TODO action? opened/closed??
        summary=f"opened PR {title}",
        eid="pull_request_" + url,
        is_bot=is_bot,
    )


def _parse_release(d: Dict) -> Event:
    tag = d["tag_name"]
    return Event(  # type: ignore[misc]
        **_parse_common(d),
        summary=f"released {tag}",
        eid="release_" + tag,
    )


def _parse_commit_comment(d: Dict) -> Event:
    url = d["url"]
    return Event(  # type: ignore[misc]
        **_parse_common(d),
        summary=f"commented on {url}",
        eid="commoit_comment_" + url,
    )
