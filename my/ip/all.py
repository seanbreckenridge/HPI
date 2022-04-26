"""
Combines IPs from data exports which include IP addresses
"""

REQUIRES = ["git+https://github.com/seanbreckenridge/ipgeocache"]

from typing import Iterator

from my.ip.common import IP  # type: ignore[import]

from my.core.common import LazyLogger

logger = LazyLogger(__name__)


# can add more sources here, or disable them through core.disabled_modules
def ips() -> Iterator[IP]:
    from . import facebook
    from . import discord
    from . import blizzard

    yield from facebook.ips()
    yield from discord.ips()
    yield from blizzard.ips()
