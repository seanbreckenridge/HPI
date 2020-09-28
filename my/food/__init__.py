# alias 'water=python3 -c "from my.food import prompt, Water; prompt(Water)"'
from ..body import prompt
from .water import Water, water
from .calories import food, Food


def stats():
    from ..core import stat

    return {
        **stat(food),
        **stat(water),
    }
