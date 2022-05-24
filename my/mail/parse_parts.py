"""
Some helper functions/constants for parsing message subparts/ignoring certain content types
"""

from typing import Iterator, Tuple, Set, Union, Any, Literal
from email.message import Message

# explicity ignored types, anything else sends a warning
IGNORED_CONTENT_TYPES = {
    "text/calendar",
    "application/ics",
    "application/pdf",
    "application/octet-stream",
    "application/octetstream",
    "text/csv",
    "application/json",
    "application/zip",
    "application/x-zip-compressed",
    "application/msword",
    "multipart/alternative",
    "application/postscript",
    "text/x-vcard",
    "multipart/parallel",  # not sure what the best way to parse this is
}

IGNORED_CONTENT_PREFIXES: Set[str] = {
    "application/vnd",
    "application/x-apple",
    "application/x-iwork",
    "image",
    "audio",
    "video",
}


def get_message_parts(m: Message) -> Iterator[Message]:
    # since walk returns both multiparts and their children
    # we can ignore the multipart and return all individual parts
    #
    # if single type, it just returns the message itself
    for part in m.walk():
        if not part.is_multipart():
            yield part


EmailText = Literal["html", "text"]


EmailTextOrContentType = Union[EmailText, str]


def tag_message_subparts(
    msg: Message,
) -> Iterator[Tuple[Any, EmailTextOrContentType]]:
    for message_part in get_message_parts(msg):
        content_type = message_part.get_content_type()
        payload = message_part.get_payload()

        # known ignored content types
        if content_type in IGNORED_CONTENT_TYPES:
            yield payload, content_type

        if any(
            [content_type.startswith(prefix) for prefix in IGNORED_CONTENT_PREFIXES]
        ):
            yield payload, content_type

        if content_type.startswith("text") and "html" in content_type:
            yield payload, "html"
        elif content_type == "text/plain":
            yield payload, "text"
        else:
            # unknown ignored content types
            yield payload, content_type
