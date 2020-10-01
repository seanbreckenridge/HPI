from more_itertools import ilen, last

from my.browsing import inputs, history


def test_browsing_contents():

    # only test the live file
    def only_live():
        return [last(inputs())]

    assert ilen(history(from_paths=only_live)) > 100
