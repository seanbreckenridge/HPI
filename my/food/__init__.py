from ..core import Stats

from ..body_log import prompt
from .water import Water, water
from .calories import food, Food


def stats() -> Stats:
    from ..core import stat

    return {
        **stat(food),
        **stat(water),
    }
