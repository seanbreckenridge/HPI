from more_itertools import ilen

from my.location.ip import ips


def test_ips() -> None:
    assert ilen(ips()) > 10
