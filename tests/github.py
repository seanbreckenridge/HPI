from more_itertools import ilen

from my.github.all import events

# todo test against stats? not sure.. maybe both

def test_gdpr():
    import my.github.gdpr as gdpr
    assert ilen(gdpr.events()) > 100


def test():
    assert ilen(events()) > 100
