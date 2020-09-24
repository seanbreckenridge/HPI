from my.money import balances, transactions
from more_itertools import ilen


def test_money():
    assert ilen(balances()) >= 1
    assert ilen(transactions()) >= 1
