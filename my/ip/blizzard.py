from typing import Iterator

from my.core.source import import_source
from my.ip.common import IP  # type: ignore[import]


@import_source(module_name="my.blizzard.gdpr")
def ips() -> Iterator[IP]:
    from my.blizzard.gdpr import events as blizzard_events

    for e in blizzard_events():
        if e.event_tag == "Activity History":
            yield IP(dt=e.dt, addr=e.metadata[-2])
