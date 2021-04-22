from my.ipython import _parse_database


def test_ipython():
    # use the live database in XDG_DATA_HOME
    db = list(_parse_database(""))
    assert len(db) > 1
    item = db[0]
    assert not isinstance(item, Exception)
    assert bool(item.command.strip())
