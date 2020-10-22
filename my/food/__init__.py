# alias 'water=python3 -c "from my.food import prompt, Water; prompt(Water)"'

from ..core import Stats

from ..body import prompt
from .water import Water, water
from .calories import food, Food


def stats() -> Stats:
    from ..core import stat

    return {
        **stat(food),
        **stat(water),
    }
