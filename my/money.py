"""
Gets Transactions/Historical account balance (banking/finances) using
https://github.com/seanbreckenridge/mint
"""

from typing import Tuple, List
from functools import lru_cache

from budget import data
from budget.analyze import cleaned_snapshots, Snapshot, Transaction
from more_itertools import last

from .core import Stats


@lru_cache(1)
def _data() -> Tuple[List[Snapshot], List[Transaction]]:
    """
    Get data from the budget module (data is handled by that/environment variables)
    see https://github.com/seanbreckenridge/mint
    """
    return data()


def balances() -> List[Snapshot]:
    """
    Return all the balance snapshots, tracked in the git hitsory
    """
    bal_snapshots, _ = _data()
    bal_snapshots.sort(key=lambda t: t.at)
    return list(cleaned_snapshots(sorted_snapshots=bal_snapshots))


def balance() -> Snapshot:
    """
    Return my current account balance
    """
    return last(balances())


def transactions() -> List[Transaction]:
    """
    Return all transactions (me buying things) I've made. Merges data from all of my different bank accounts
    """
    _, transactions = _data()
    transactions.sort(key=lambda t: t.on)
    return transactions


def stats() -> Stats:
    from .core import stat

    return {
        **stat(balances),
        **stat(transactions),
    }
