from .commits import commits, repos


def stats():
    from ..core import stat

    return {
        **stat(commits),
        **stat(repos),
    }
