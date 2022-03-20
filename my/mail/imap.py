"""
Parses my locally synced IMAP email files, using mbsync
https://isync.sourceforge.io/mbsync.html
Uses https://github.com/SpamScope/mail-parser to parse the mail
"""

REQUIRES = ["mail-parser", "dateparser"]

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import mail as user_config  # type: ignore[attr-defined]

from pathlib import Path
from typing import (
    Iterator,
    List,
)


from my.core import Stats, Paths, dataclass, get_files
from .common import Email, unique_mail



@dataclass
class config(user_config.imap):
    # path[s]/glob to the the individual email files -- searches recusively
    mailboxes: Paths


def mailboxes() -> List[Path]:
    return list(get_files(config.mailboxes))


def files() -> Iterator[Path]:
    for box in mailboxes():
        for path in box.rglob("*"):
            if not path.is_file():
                continue
            if path.stem.startswith("."):
                continue
            yield path


def raw_mail() -> Iterator[Email]:
    for m in map(Email.safe_parse_path, files()):
        if m is not None:
            yield m



def mail() -> Iterator[Email]:
    yield from unique_mail(raw_mail())


def stats() -> Stats:
    from my.core import stat

    return {**stat(mail)}
