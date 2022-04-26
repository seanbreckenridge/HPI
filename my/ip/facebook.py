from typing import Iterator, List
from pathlib import Path

from my.ip.common import IP, drop_private  # type: ignore[import]

from my.core.source import import_source
from my.core.common import mcachew, LazyLogger, Stats


logger = LazyLogger(__name__)


def _cachew_depends_on() -> List[float]:
    from my.facebook.gdpr import config as facebook_config

    return [p.stat().st_mtime for p in Path(facebook_config.gdpr_dir).rglob("*")]


@import_source(module_name="my.facebook.gdpr")
def ips() -> Iterator[IP]:
    from my.facebook.gdpr import (
        AdminAction,
        UploadedPhoto,
        events as facebook_events,
    )

    @mcachew(
        depends_on=_cachew_depends_on,
        logger=logger,
    )
    def _facebook_ips() -> Iterator[IP]:
        for e in facebook_events():
            if isinstance(e, AdminAction) or isinstance(e, UploadedPhoto):
                if not isinstance(e, Exception):
                    yield IP(dt=e.dt, addr=e.ip)

    yield from drop_private(_facebook_ips())


def stats() -> Stats:
    from my.core import stat

    return {**stat(ips)}
