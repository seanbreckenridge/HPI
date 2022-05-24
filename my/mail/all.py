from typing import Iterator
from itertools import chain

from my.core import Stats
from my.core.source import import_source

REQUIRES = ["mail-parser", "dateparser"]


src_imap = import_source(module_name="my.mail.imap")
src_mbox = import_source(module_name="my.mail.mbox")


# top-level import -- this whole module requires mail-parser/dateparser
from .common import Email, unique_mail, MessagePart


@src_imap
def _mail_imap() -> Iterator[Email]:
    from . import imap

    return imap.mail()


@src_mbox
def _mail_mbox() -> Iterator[Email]:
    from . import mbox

    return mbox.mail()


# NOTE: you can comment out the sources you don't want
def mail() -> Iterator[Email]:
    yield from unique_mail(
        chain(
            _mail_mbox(),
            _mail_imap(),
        )
    )


def mail_subparts() -> Iterator[MessagePart]:
    for m in mail():
        yield from m.subparts


def stats() -> Stats:
    from my.core import stat

    return {**stat(mail)}
