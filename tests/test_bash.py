import os
from pathlib import Path

from my.bash import _parse_file

from .common import data


def test_single_file() -> None:
    history_file = data("bash/history")
    history = list(_parse_file(history_file))
    assert len(history) == 4
    assert history[0].command == "ls"
    assert history[1].command == "git status"
    assert (
        history[2].command
        == '''echo "$(
date
uname
)"'''
    )

    assert history[3].command == "ls"
