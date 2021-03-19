from typing import Iterator
from tupletally.models import Water

# reuse config from my.body
from ..body import glob_namedtuple_with_config


def water() -> Iterator[Water]:
    yield from glob_namedtuple_with_config(Water)
