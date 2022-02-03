"""
Parses my locally synced IMAP email files, using mbsync
https://isync.sourceforge.io/mbsync.html
Uses https://github.com/SpamScope/mail-parser to parse the mail
"""

REQUIRES = ["mail-parser", "dateparser"]

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import mail as user_config  # type: ignore[attr-defined]

import logging
from pathlib import Path
from email.parser import Parser
from typing import (
    Iterator,
    List,
    Optional,
    Dict,
    Any,
    cast,
)
from datetime import datetime

import dateparser
from mailparser import MailParser  # type: ignore[import]
from mailparser.exceptions import MailParserReceivedParsingError  # type: ignore[import]
from more_itertools import unique_everseen

from my.core import Stats, LazyLogger, Paths, dataclass, get_files

# silence all mailparser logs
# https://stackoverflow.com/a/55396144
mlog = logging.getLogger("mailparser")
for handler in mlog.handlers.copy():
    mlog.removeHandler(handler)
mlog.addHandler(logging.NullHandler())
mlog.propagate = False

logger = LazyLogger(__name__)


@dataclass
class config(user_config.imap):
    # path[s]/glob to the the mailboxes/IMAP files
    mailboxes: Paths


class Email(MailParser):
    """
    subclass of the mailparser which
    supports serialization by my.core.serialize
    along with a few other convenience functions
    """

    # note: The 'message' property on this class
    # is the stdlib email.Message class:
    # https://docs.python.org/3/library/email.message.html#module-email.message
    def __init__(self, message: Parser) -> None:
        super().__init__(message=message)
        self.filepath: Optional[Path] = None
        self._dt: Optional[datetime] = None  # property to cache datetime result

    @property
    def dt(self) -> Optional[datetime]:
        """
        Try to parse datetime if mail date wasn't in RFC 2822 format
        """
        if self._dt is not None:
            return self._dt
        # If date was parsed properly by mailparser
        d = self.date
        if isinstance(d, datetime):
            self._dt = d
            return self._dt
        if "Date" in self.headers:
            # even if this fails (returns None), we should save the None, since it means
            # that the dateparser call (which can take a while) doesn't have to run again
            self._dt = dateparser.parse(self.headers["Date"])
            return self._dt
        return None

    def _serialize(self) -> Dict[str, Any]:
        return {
            "filepath": self.filepath,
            "bcc": self.bcc,
            "cc": self.cc,
            "date": self.dt,
            "date_utc": self.date_utc,
            "delivered_to": self.delivered_to,
            "from": self.from_,
            "message_id": self.message_id,
            "received": self.received,
            "reply_to": self.reply_to,
            "subject": self.subject,
            "to": self.to,
            "by": self.by,
            "envelope_from": self.envelope_from,
            "envelope_sender": self.envelope_sender,
            "for": getattr(self, "for"),
            "hop": self.hop,
            "with": getattr(self, "with"),
            "body": self.body,
            "body_html": self.body_html,
            "body_plain": self.body_plain,
            "attachments": self.attachments,
            "sender_ip_address": self.sender_ip_address,
            "to_domains": self.to_domains,
        }

    @classmethod
    def safe_parse(cls, path: Path) -> Optional["Email"]:
        """
        Alternate constructor which catches common
        errors/bugs that mailparser could raise
        """
        try:
            m = cls.from_file(path)  # calls MailParser.from_file
            m.filepath = path
            return cast(Email, m)
        except UnicodeDecodeError as e:
            logger.debug(f"While parsing {path}: {e}")
        except MailParserReceivedParsingError as e:
            logger.debug(f"While parsing {path}: {e}")
        except AttributeError as e:
            # error in the 'find_between' function when
            # the epilogue fails to be parse
            if str(e) == "'NoneType' object has no attribute 'index'":
                logger.debug(f"While parsing {path}: {e}")
            else:
                raise e
        return None


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
    for m in map(Email.safe_parse, files()):
        if m is not None:
            yield m


def mail() -> Iterator[Email]:
    # remove duplicates (from a file being
    # in multiple boxes and the 'default' inbox)
    # some formats won't have a message id,
    # but hopefully the date/subject creates a unique
    # key in that case
    yield from unique_everseen(
        raw_mail(),
        key=lambda m: (
            m.subject_json,
            m.message_id_json,
            m.dt,
        ),
    )


def stats() -> Stats:
    from my.core import stat

    return {**stat(mail)}
