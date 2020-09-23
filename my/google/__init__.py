#!/usr/bin/env python3

"""
my comment:
Need to develop a strategy for removing intermediate takeout
exports?

since a lot of the data is repeated, we don't need *all*
the takeouts, just need enough to merge data from old
ones and new ones, without taking up tons of space
on disk

perhaps keep the 3 most recent takeouts, the first takeout
and then intermediate takeouts going back at 6 month intervals

oldest takeout
2 takeouts from 2019
2 takeouts from 2020
2 takeouts from 2021
....
....
3 most recent takeouts

*maaybe* this isn't needed at all, and I should just
keep all the takeouts (they're about 195MB each)
"""

# karlicoss comment:
# TODO might be a good idea to merge across multiple takeouts...
# perhaps even a special takeout module that deals with all of this automatically?
# e.g. accumulate, filter and maybe report useless takeouts?

from .paths import get_last_takeout
from .takeout_parser import Results, parse_takeout


# temporary basic entrypoint
def events() -> Results:
    yield from parse_takeout(get_last_takeout())


def stats():
    pass
    # from .core import stat

    # return {
    #    **stat(events),
    # }
