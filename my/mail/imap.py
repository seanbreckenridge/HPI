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
    Callable,
    Optional,
    List,
)


from my.core import Stats, Paths, dataclass, get_files, make_config
from .common import Email, unique_mail


@dataclass
class imap_conf(user_config.imap):
    # path[s]/glob to the the individual email files -- searches recusively
    mailboxes: Paths

    # filter function which filters the input paths
    filter_path: Optional[Callable[[Path], bool]] = None


config = make_config(imap_conf)


def mailboxes() -> List[Path]:
    return list(get_files(config.mailboxes))


def _files() -> Iterator[Path]:
    for box in mailboxes():
        for path in box.rglob("*"):
            if not path.is_file():
                continue
            if path.stem.startswith("."):
                continue
            yield path


def files() -> Iterator[Path]:
    if config.filter_path is None:
        yield from _files()
    else:
        assert callable(config.filter_path)
        yield from filter(config.filter_path, _files())


def raw_mail() -> Iterator[Email]:
    for m in map(Email.safe_parse_path, files()):
        if m is not None:
            yield m


def mail() -> Iterator[Email]:
    yield from unique_mail(raw_mail())


def stats() -> Stats:
    from my.core import stat

    return {**stat(mail)}
