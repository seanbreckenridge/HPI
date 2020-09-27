from more_itertools import ilen

import my.github.gdpr as gdpr
from my.github.all import events

# todo test against stats? not sure.. maybe both


def test_gdpr():
    assert ilen(gdpr.events()) > 100


def test_github():
    assert ilen(events()) > 100
