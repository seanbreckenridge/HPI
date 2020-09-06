from more_itertools import ilen

from my.browsing import inputs, history


def test_browsing_inputs():
    assert ilen(inputs()) >= 2  # export + live file


def test_browsing_contents():
    # only test the live file
    def only_live():
        return list(inputs())[-1]

    assert ilen(history()) > 10
