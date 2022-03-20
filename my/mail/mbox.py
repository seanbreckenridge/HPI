"""
Parses local mbox files
"""

REQUIRES = ["mail-parser", "dateparser"]

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import mail as user_config  # type: ignore[attr-defined]

import mailbox
from pathlib import Path
from typing import List, Iterator, Optional, Sequence, IO, Any

from my.core import Stats, Paths, dataclass, get_files
from my.core.common import LazyLogger

from my.mail.imap import Email, unique_mail


logger = LazyLogger(__name__)


@dataclass
class config(user_config.mbox):
    # path[s]/glob to the mbox file directory
    mailboxes: Paths

    # any additional extensions to ignore -- by default includes .msf, .dat, .log
    exclude_extensions: Optional[Sequence[str]] = None


def mailboxes() -> List[Path]:
    return list(get_files(config.mailboxes))


DEFAULT_EXCLUDED_EXTENSIONS = {
    ".msf",
    ".log",
    ".dat",
}


def files() -> Iterator[Path]:
    excluded_ext = set(DEFAULT_EXCLUDED_EXTENSIONS)
    if config.exclude_extensions:
        for ext in config.exclude_extensions:
            excluded_ext.add(ext)

    for box in mailboxes():
        for path in box.rglob("*"):
            if path.stem.startswith("."):
                continue
            if path.is_file():
                if path.suffix not in excluded_ext:
                    yield path


def _try_decode(buf: bytes) -> str:
    try:
        return buf.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return buf.decode("iso-8859-1")
        except UnicodeDecodeError:
            return buf.decode("latin-1")


def _decode_msg(msg: IO[Any]) -> mailbox.mboxMessage:
    """
    Custom decode function

    by default this uses 'ascii' which can cause fatal errors
    on UnicodeDecodeErrors
    """
    msg_str = _try_decode(msg.read())
    return mailbox.mboxMessage(mailbox.Message(msg_str))


def _iter_mailbox(file: Path) -> Iterator[Email]:
    mbox = mailbox.mbox(
        str(file),
        factory=_decode_msg,
        create=False,
    )
    mbox_itr = iter(mbox)
    while True:
        try:
            mbox_message = next(mbox_itr)
            email = Email.safe_parse(mbox_message, display_filename=file)
            if email is not None:
                email.filepath = file
                yield email
        except StopIteration:
            break
        except Exception as ex:
            logger.warning(
                f"Unexpected error while parsing {file}: {ex}... no way to continue parsing mbox file...",
                exc_info=ex,
            )


def raw_mail() -> Iterator[Email]:
    for file in files():
        assert file.exists()  # sanity check -- make sure were not creating mboxes
        yield from _iter_mailbox(file)


def mail() -> Iterator[Email]:
    yield from unique_mail(raw_mail())


def stats() -> Stats:
    from my.core import stat

    return {**stat(mail)}
