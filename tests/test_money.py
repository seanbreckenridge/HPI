from more_itertools import ilen

from my.money import balances, transactions


def test_money():
    assert ilen(balances()) >= 1
    assert ilen(transactions()) >= 1
