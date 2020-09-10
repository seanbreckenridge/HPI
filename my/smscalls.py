"""
Phone calls and SMS messages
"""

# Note: these are exported by https://play.google.com/store/apps/details?id=com.riteshsahu.SMSBackupRestore&hl=en_US
# those save to google drive, which sync down to my machine using https://github.com/odeke-em/drive
#
# my.config.smscalls is set to that location, see: https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py

from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple, Iterator, Set

from lxml import etree  # type: ignore

from .core.common import get_files

from my.config import smscalls as config  # type: ignore


class Call(NamedTuple):
    dt: datetime
    duration_s: int
    who: str
    phone_number: str

    @property
    def summary(self) -> str:
        return f"talked with {self.who} for {self.duration_s} secs"


class Message(NamedTuple):
    dt: datetime
    who: str
    message: str
    phone_number: str  # phone number
    from_me: bool


def messages() -> Iterator[Message]:
    files = get_files(config.export_path, glob="sms-*.xml")

    emitted: Set[datetime] = set()
    for p in files:
        for c in _extract_messages(p):
            if c.dt in emitted:
                continue
            emitted.add(c.dt)
            yield c


def _extract_messages(path: Path) -> Iterator[Message]:
    tr = etree.parse(str(path))
    for mxml in tr.findall("sms"):
        yield Message(
            dt=_parse_date(mxml.get("date")),
            who=mxml.get("contact_name"),
            message=mxml.get("body"),
            phone_number=mxml.get("address"),
            from_me=mxml.get("type") == "2",  # 1 is recieved message, 2 is sent message
        )


def calls() -> Iterator[Call]:
    files = get_files(config.export_path, glob="calls-*.xml")

    # TODO always replacing with the latter is good, we get better contact names??
    emitted: Set[datetime] = set()
    for p in files:
        for c in _extract_calls(p):
            if c.dt in emitted:
                continue
            emitted.add(c.dt)
            yield c


def _extract_calls(path: Path) -> Iterator[Call]:
    tr = etree.parse(str(path))
    for cxml in tr.findall("call"):
        # TODO we've got local tz here, not sure if useful..
        # ok, so readable date is local datetime, cahnging throughout the backup
        yield Call(
            dt=_parse_date(cxml.get("date")),
            duration_s=int(cxml.get("duration")),
            phone_number=cxml.get("number"),
            who=cxml.get("contact_name")  # TODO number if contact is unavail??
            # TODO type? must be missing/outgoing/incoming
        )


def _parse_date(date: str):
    return datetime.fromtimestamp(int(date) / 1000, tz=timezone.utc)
