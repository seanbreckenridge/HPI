#!/usr/bin/env python3

# karlicoss comment:
# TODO might be a good idea to merge across multiple takeouts...
# perhaps even a special takeout module that deals with all of this automatically?
# e.g. accumulate, filter and maybe report useless takeouts?

from itertools import chain
from typing import Set

from my.core.common import Stats, LazyLogger, mcachew
from my.core.cachew import cache_dir

from .paths import takeout_input_directories
from .takeout_parser import Results, RawResults, parse_takeout

logger = LazyLogger(__name__, level="warning")


def events() -> Results:
    # parse the list of links (serialized to JSON so cachew can store it)
    # back into a list
    for event in raw_events():
        if hasattr(event, "parse_links"):
            yield event.parse_links()  # type: ignore[union-attr]
        else:
            yield event  # type: ignore[misc]


@mcachew(
    cache_path=lambda: str(cache_dir() / "_merged_google_events"),
    depends_on=lambda: list(sorted(takeout_input_directories())),
    force_file=True,
    logger=logger,
)
def raw_events() -> RawResults:
    yield from merge_events(*map(parse_takeout, takeout_input_directories()))


def merge_events(*sources: RawResults) -> RawResults:
    emitted: Set[int] = set()
    for event in chain(*sources):
        if isinstance(event, Exception):
            yield event
            continue
        key: int = int(event.dt.timestamp())
        if key in emitted:
            continue
        emitted.add(key)
        yield event


def stats() -> Stats:
    from my.core import stat

    return {
        **stat(events),
    }
