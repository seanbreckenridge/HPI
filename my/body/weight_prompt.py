"""
Prompts the user for weight and writes to logfile
"""

import sys

from pprint import pprint
from datetime import datetime

from prompt_toolkit import prompt
from prompt_toolkit.validation import Validator

from .weight import Entry


def is_float(text: str) -> bool:
    try:
        float(text)
        return True
    except ValueError:
        return False


def weight_prompt_tui() -> float:
    try:
        weight_str = prompt(
            "Enter Weight (lbs) > ",
            validator=Validator.from_callable(
                is_float, error_message="Could not convert to float"
            ),
        )
    except (EOFError, KeyboardInterrupt) as e:
        print()
        sys.exit(1)
    return float(weight_str)


# add to rc file:
# alias 'weight=python -c "from my.body.weight_prompt import prompt_and_write; prompt_and_write()"'
def prompt_and_write() -> None:
    e = Entry(dt=datetime.now(), value=weight_prompt_tui())
    pprint(f"Writing {e}")
    e.write()
