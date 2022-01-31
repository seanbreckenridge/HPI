from my.ipython import _parse_database

from .common import data


def test_ipython() -> None:
    ipython_db = str(data("ipython.sqlite"))
    cmds = list(_parse_database(ipython_db))
    assert len(cmds) == 13
    item = cmds[1]
    assert not isinstance(item, Exception)
    assert item.command == "fac(121)"
