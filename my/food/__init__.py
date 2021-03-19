from my.core import Stats

# TODO: remove this file, move to their individual modules
from .water import Water, water
from .calories import food, Food


def stats() -> Stats:
    from my.core import stat

    return {
        **stat(food),
        **stat(water),
    }
