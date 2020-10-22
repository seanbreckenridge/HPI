from ..core import Stats

from .commits import commits, repos


def stats() -> Stats:
    from ..core import stat

    return {
        **stat(commits),
        **stat(repos),
    }
