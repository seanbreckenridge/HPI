import os
from pathlib import Path

from my.bash import _parse_file

test_dir = os.path.dirname(os.path.abspath(__file__))
history_file = Path(os.path.join(test_dir, "bash", "history"))


def test_single_file() -> None:
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
