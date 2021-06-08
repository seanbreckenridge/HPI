from typing import Iterable
from itertools import chain

from more_itertools import ilen

from my.albums import to_listen, history, _albums_cached, Album, CANT_FIND


def test_albums() -> None:
    assert ilen(history()) > 1
    assert ilen(to_listen()) > 1


cant_find_func = lambda a: a.note == CANT_FIND

# make sure albums that I can't find (are lost media or unavailable online)
# aren't in the history and to_listen results
def test_cant_find() -> None:
    cant_find: Iterable[Album] = chain(
        filter(cant_find_func, history()),
        filter(cant_find_func, to_listen()),
    )
    assert ilen(cant_find) == 0
