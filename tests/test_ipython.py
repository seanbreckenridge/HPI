from my.ipython import _parse_database

from .common import data

import pytest

from IPython.core.history import HistoryAccessor  # type: ignore[import]


# https://github.com/ipython/ipython/issues/13666
def accessor_works() -> bool:
    ipython_db = str(data("ipython.sqlite"))
    hist = HistoryAccessor(hist_file=ipython_db)
    try:
        hist.get_last_session_id()
        return True
    except Exception:
        return False


@pytest.mark.skipif(not accessor_works(), reason="ipython historyaccessor failed")
def test_ipython() -> None:
    ipython_db = str(data("ipython.sqlite"))
    cmds = list(_parse_database(ipython_db))
    assert len(cmds) == 13
    item = cmds[1]
    assert not isinstance(item, Exception)
    assert item.command == "fac(121)"
