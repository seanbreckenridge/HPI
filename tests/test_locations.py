from more_itertools import ilen

from my.location.all import locations

from my.location.gpslogger import history


def test_locations() -> None:
    assert ilen(locations()) > 100


def test_gpslogger() -> None:
    assert ilen(history()) > 100
