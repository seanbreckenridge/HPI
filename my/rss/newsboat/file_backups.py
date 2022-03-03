"""
Parses backups of my newsboat rss file
"""

from datetime import datetime
from typing import NamedTuple, Literal

from my.core import Paths, dataclass
from my.config import rss as user_config  # type: ignore[attr-defined]


@dataclass
class config(user_config.newsboat.file_backups):
    # path[s]/glob to the backed up newsboat rss files
    # for an example of expected input, see
    # https://github.com/seanbreckenridge/HPI-personal/blob/8fb96882b492425280e84b8931b40948c3b5fe8c/jobs/linux/backup_newsboat.job
    export_path: Paths


from typing import Tuple, Iterator, Dict, Set
from pathlib import Path

from more_itertools import last
from my.core.common import get_files, Stats

Subscriptions = Set[str]

# snapshot of subscriptions at time
SubscriptionState = Tuple[datetime, Subscriptions]


def inputs() -> Iterator[Tuple[datetime, Path]]:
    rss_backups = get_files(config.export_path)
    for rssf in rss_backups:
        dt = datetime.strptime(rssf.stem, "%Y%m%dT%H%M%SZ")
        yield (dt, rssf)


def _subscription_history() -> Iterator[SubscriptionState]:
    for dt, p in inputs():
        yield dt, set(_parse_subscription_file(p))


def _parse_subscription_file(p: Path) -> Iterator[str]:
    for line in p.read_text().splitlines():
        ln = line.strip()
        if ln:
            yield ln.strip().split()[0]


def subscriptions() -> Subscriptions:
    return last(sorted(list(_subscription_history()), key=lambda s: s[0]))[1]


Action = Literal["added", "removed"]


class RssEvent(NamedTuple):
    url: str
    dt: datetime
    action: Action


def events() -> Iterator[RssEvent]:
    """
    Keeps track of everything I ever subscribed to.
    In addition, keeps track of unsubscribed as well (so you'd remember when and why you unsubscribed)
    """
    current_state: Dict[str, datetime] = {}
    subs = sorted(list(_subscription_history()), key=lambda s: s[0])

    for dt, slist in subs:
        subset: Subscriptions = set()
        # for each subscription
        for sb in slist:
            subset.add(sb)
            if sb in current_state:
                continue
            current_state[sb] = dt
            yield RssEvent(url=sb, dt=dt, action="added")

        # check if any were removed
        for sb in list(current_state):
            if sb not in subset:
                yield RssEvent(url=sb, dt=dt, action="removed")
                del current_state[sb]


def stats() -> Stats:
    from my.core import stat

    return {
        **stat(subscriptions),
        **stat(events),
    }
