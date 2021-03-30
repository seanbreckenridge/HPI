"""
Parses backups of my newsboat rss file
"""

from datetime import datetime
from typing import NamedTuple

from my.core import Paths, dataclass
from my.config import newsboat as user_config  # type: ignore[attr-defined]


@dataclass
class config(user_config):
    # path[s]/glob to the backed up newsboat rss files
    export_path: Paths


from typing import Tuple, Sequence, Iterator, Dict, Set
from pathlib import Path

from my.core.common import listify, get_files, Stats

Subscription = str
Subscriptions = Sequence[str]

# snapshot of subscriptions at time
SubscriptionState = Tuple[datetime, Subscriptions]


@listify
def inputs() -> Sequence[Tuple[datetime, Path]]:  # type: ignore[misc]
    rss_backups = get_files(config.export_path)
    for rssf in rss_backups:
        dt = datetime.strptime(rssf.stem, "%Y%m%dT%H%M%SZ")
        yield (dt, rssf)


def current_subscriptions() -> Subscriptions:
    subs = sorted(list(subscription_history()), key=lambda s: s[0])
    return subs[-1][1]


def subscription_history() -> Iterator[SubscriptionState]:
    for dt, p in inputs():
        yield dt, _parse_subscription_file(p)


@listify
def _parse_subscription_file(p: Path) -> Sequence[Subscription]:  # type: ignore[misc]
    for line in p.read_text().splitlines():
        ln = line.strip()
        if ln:
            yield ln.strip().split()[0]


class RssEvent(NamedTuple):
    url: Subscription
    dt: datetime
    # type/false for added/removed
    added: bool


def events() -> Iterator[RssEvent]:
    """
    Keeps track of everything I ever subscribed to.
    In addition, keeps track of unsubscribed as well (so you'd remember when and why you unsubscribed)
    """
    current_state: Dict[Subscription, datetime] = {}
    subs = sorted(list(subscription_history()), key=lambda s: s[0])

    for dt, slist in subs:
        subset: Set[Subscription] = set()
        # for each subscription
        for sb in slist:
            subset.add(sb)
            if sb in current_state:
                continue
            current_state[sb] = dt
            yield RssEvent(url=sb, dt=dt, added=True)

        # check if any were removed
        for sb in list(current_state):
            if sb not in subset:
                yield RssEvent(url=sb, dt=dt, added=False)
                del current_state[sb]


def stats() -> Stats:
    from my.core import stat

    return {
        **stat(current_subscriptions),
        **stat(subscription_history),
        **stat(events),
    }
