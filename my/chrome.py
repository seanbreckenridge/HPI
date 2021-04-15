"""
Exposes Chrome browser history, parses using promnesia
"""

# this is very basic, it just calls the functions from promnesia to grab this
# incase I want to inspect my chrome history

# TODO: Combine this into browsing? need to figure out nested configs

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import chrome as user_config  # type: ignore[attr-defined]
from my.core import Paths, dataclass


@dataclass
class config(user_config):
    # path[s]/glob to the exported firefox history sqlite files
    export_path: Paths


from pathlib import Path
from typing import Sequence, Iterator

from my.core.common import get_files

# just uses the promnesia indexer to grab info
from promnesia.common import Visit
from promnesia.sources.browser import _index_db


def inputs() -> Sequence[Path]:
    """Returns all backed up ffexport databases"""
    return get_files(config.export_path)


# TODO: cachew? probably not needed, I barely use chrome
def history() -> Iterator[Visit]:
    emitted = set()  # type: ignore
    for db in inputs():
        yield from _index_db(db, emitted)
