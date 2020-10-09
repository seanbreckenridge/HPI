from contextlib import contextmanager
from pathlib import Path


def disable_cachew():
    try:
        import cachew
    except ImportError:
        # nothing to disable
        return

    from cachew import settings

    settings.ENABLE = False


@contextmanager
def disabled_cachew():
    try:
        import cachew
    except ImportError:
        # nothing to disable
        yield
        return
    from cachew.extra import disabled_cachew

    with disabled_cachew():
        yield


def cache_dir() -> Path:
    """
    Base directory for cachew.
    To override, add to your config file:
    class config:
        cache_dir = '/your/custom/cache/path'
    """
    from .core_config import config

    common_config = config.cache_dir

    cdir = getattr(common_config, "cache_dir", None)
    if cdir is None:
        # TODO fallback to default cachew dir instead?
        return Path("/tmp/cachew")
    else:
        return Path(cdir)
