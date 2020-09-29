from more_itertools import ilen

import my.github.gdpr as gdpr
import my.github.ghexport as ghexport

# todo test against stats? not sure.. maybe both


def test_gdpr():
    assert ilen(gdpr.events()) > 100


def test_github():
    assert ilen(ghexport.events()) > 100
    assert ilen(ghexport.all_events()) > ilen(ghexport.events())
