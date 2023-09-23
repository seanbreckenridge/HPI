import logging
from pathlib import Path
from email.message import Message
from typing import (
    List,
    Tuple,
    TextIO,
    Iterator,
    Optional,
    Union,
    Dict,
    Any,
    cast,
)
from datetime import datetime
from dataclasses import dataclass

import dateparser
from mailparser import MailParser  # type: ignore[import]
from mailparser.exceptions import MailParserReceivedParsingError  # type: ignore[import]
from more_itertools import unique_everseen

from my.core import LazyLogger, __NOT_HPI_MODULE__  # noqa: F401

from .parse_parts import tag_message_subparts

REQUIRES = ["mail-parser", "dateparser"]

# silence all mailparser logs
# https://stackoverflow.com/a/55396144
mlog = logging.getLogger("mailparser")
for handler in mlog.handlers.copy():
    mlog.removeHandler(handler)
mlog.addHandler(logging.NullHandler())
mlog.propagate = False

logger = LazyLogger(__name__)


@dataclass
class MessagePart:
    content_type: str
    payload: Any
    _email: "Email"


class Email(MailParser):
    """
    subclass of the mailparser which
    supports serialization by my.core.serialize
    along with a few other convenience functions
    """

    # note: The 'message' property on this class
    # is the stdlib email.Message class:
    # https://docs.python.org/3/library/email.message.html#module-email.message
    def __init__(self, message: Message) -> None:
        super().__init__(message=message)
        self.filepath: Optional[Path] = None
        self._dt: Optional[datetime] = None  # property to cache datetime result
        self._dateparser_failed: bool = False  # if dateparser previously failed

    @property
    def dt(self) -> Optional[datetime]:
        """
        Try to parse datetime if mail date wasn't in RFC 2822 format
        """
        if self._dt is not None:
            return self._dt
        if self._dateparser_failed:
            return None
        # If date was parsed properly by mailparser
        d = self.date
        if isinstance(d, datetime):
            self._dt = d
            return self._dt
        if "Date" in self.headers:
            dateparser_res: Optional[datetime] = dateparser.parse(self.headers["Date"])
            # if this failed to parse, save it on the object
            if dateparser_res is None:
                self._dateparser_failed = True
                return None
            else:
                self._dt = dateparser_res
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

    @property
    def description(self) -> str:
        return f"""From: {describe_persons(self.from_)}
To: {describe_persons(self.to)}
Subject: {self.subject}"""

    @classmethod
    def safe_parse(
        cls, fp: Union[str, bytes, Message, TextIO], display_filename: Path
    ) -> Optional["Email"]:
        try:
            if isinstance(fp, bytes):
                m = cls.from_bytes(fp)
            elif isinstance(fp, str):
                m = cls.from_string(fp)
            elif isinstance(fp, Message):
                # convert the email.Message (or a subclass) to this class
                m = cls(message=fp)
            else:
                m = cls.from_file_obj(fp)
            return cast(Email, m)
        except UnicodeDecodeError as e:
            logger.debug(f"While parsing {display_filename}: {e}")
        except MailParserReceivedParsingError as e:
            logger.debug(f"While parsing {display_filename}: {e}")
        except AttributeError as e:
            # error in the 'find_between' function when
            # the epilogue fails to be parse
            if str(e) == "'NoneType' object has no attribute 'index'":
                logger.debug(
                    f"While parsing {display_filename}, epilogue failed to be parsed: {e}"
                )
            else:
                logger.debug(
                    f"Unknown error while parsing {display_filename}: {e}, skipping...",
                    exc_info=e,
                )
        except Exception as e:
            logger.warning(
                f"Unknown error while parsing {display_filename}: {e}, skipping...",
                exc_info=e,
            )
        return None

    @classmethod
    def safe_parse_path(cls, path: Path) -> Optional["Email"]:
        with path.open("rb") as bf:
            m = cls.safe_parse(try_decode_buf(bf.read()), display_filename=path)
        if m is None:
            return None
        m.filepath = path
        return m

    @property
    def subparts(self) -> Iterator[MessagePart]:
        for payload, content_type in tag_message_subparts(self.message):
            yield MessagePart(
                content_type=content_type,
                payload=payload,
                _email=self,
            )


def unique_mail(emails: Iterator[Email]) -> Iterator[Email]:
    # remove duplicates (from a file being
    # in multiple boxes and the 'default' inbox)
    # some formats won't have a message id,
    # but hopefully the date/subject creates a unique
    # key in that case
    yield from unique_everseen(
        emails,
        key=lambda m: (
            m.subject_json,
            m.message_id_json,
            m.dt,
        ),
    )


def try_decode_buf(buf: bytes) -> str:
    try:
        return buf.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return buf.decode("iso-8859-1")
        except UnicodeDecodeError:
            return buf.decode("latin-1")


def describe_person(p: Tuple[str, str]) -> str:
    """
    (
        "Person",
        "emailhere@gmail.com"
    )
    converts to
    Person <emailhere@gmail.com>
    if there's no 'Person' text, it
    just becomes:
    emailhere@gmail.com
    """
    if p[0].strip():
        return f"{p[0]} <{p[1]}>"
    else:
        return p[1]


def describe_persons(m: List[Tuple[str, str]]) -> str:
    """
    >>> [('Google', 'no-reply@accounts.google.com'), ('Github', 'no-reply@github.com')]
    'Google <no-reply@accounts.google.com>, Github <no-reply@github.com>'
    """
    return ", ".join([describe_person(p) for p in m])
