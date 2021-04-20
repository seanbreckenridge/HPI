"""
Discord Data: messages and events data
"""
REQUIRES = [
    "git+https://github.com/seanbreckenridge/discord_data",
    "urlextract",
]


from pathlib import Path
from typing import List

from my.config import discord as user_config  # type: ignore[attr-defined]
from my.core import PathIsh, dataclass


@dataclass
class config(user_config):

    # path to the top level discord export directory
    # see https://github.com/seanbreckenridge/discord_data for more info
    export_path: PathIsh

    # property? functools.cached_property?
    @classmethod
    def _abs_export_path(cls) -> Path:
        return Path(cls.export_path).expanduser().absolute()


from typing import Iterator, Optional, Tuple
from my.core.common import LazyLogger, Stats, mcachew

from discord_data import merge_messages, merge_activity, Activity, Message
from urlextract import URLExtract


logger = LazyLogger(__name__, level="warning")


def _remove_suppression(text: str, first_index: int, second_index: int) -> str:
    # remove char at first index
    text = text[:first_index] + text[first_index + 1 :]
    # offset second index, since we removed a character
    second_index -= 1
    # remove character at second index
    return text[:second_index] + text[second_index + 1 :]


extractor = URLExtract()


def _remove_link_suppression(
    content: str, urls: Optional[List[Tuple[str, Tuple[int, int]]]] = None
) -> str:
    # fix content to remove discord link suppression if any links had any
    # e.g. this is a suppressed link <https://github.com>

    if urls is None:
        urls = extractor.find_urls(content, get_indices=True)

    # need to keep track to we can offset the index in the content to remove
    removed_chars = 0
    for (url_text, (start_index, end_index)) in urls:
        before_ind = (start_index - 1) - removed_chars
        after_ind = (end_index) - removed_chars
        try:
            if content[before_ind] == "<" and content[after_ind] == ">":
                content = _remove_suppression(content, before_ind, after_ind)
                removed_chars += 2
        except IndexError:  # could happen if the url didn't have braces and we hit the end of a string
            continue
    return content


def test_remove_link_suppression() -> None:
    assert _remove_suppression("<test>", 0, 5) == "test"

    # shouldn't affect this at all
    content = "https://urlextract.readthedocs.io"
    assert _remove_link_suppression(content) == content

    content = "<https://urlextract.readthedocs.io>"
    expected = content.strip("<").strip(">")
    assert _remove_link_suppression(content) == expected

    content = "Here is some text <https://urlextract.readthedocs.io>"
    expected = "Here is some text https://urlextract.readthedocs.io"
    assert _remove_link_suppression(content) == expected

    content = "text <https://urlextract.readthedocs.io> other text"
    expected = "text https://urlextract.readthedocs.io other text"
    assert _remove_link_suppression(content) == expected

    content = "t <https://urlextract.readthedocs.io> other <github.com> f <sean.fish>"
    expected = "t https://urlextract.readthedocs.io other github.com f sean.fish"
    assert _remove_link_suppression(content) == expected


def _cachew_depends_on() -> List[str]:
    return list(map(str, config._abs_export_path().iterdir()))


# reduces time by multiple minutes, after the cache is created
# HTML rendering can take quite a long time for the thousands of messages
@mcachew(depends_on=_cachew_depends_on, logger=logger)
def messages() -> Iterator[Message]:
    for msg in merge_messages(export_dir=config._abs_export_path()):
        yield Message(
            message_id=msg.message_id,
            timestamp=msg.timestamp,
            channel=msg.channel,
            content=_remove_link_suppression(msg.content),
            attachments=msg.attachments,
        )


@mcachew(depends_on=_cachew_depends_on, logger=logger)
def activity() -> Iterator[Activity]:
    yield from merge_activity(export_dir=config._abs_export_path())


def stats() -> Stats:
    from my.core import stat

    return {
        **stat(messages),
        **stat(activity),
    }
