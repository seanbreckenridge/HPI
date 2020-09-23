"""
Google Takeout exports: browsing history, search/youtube/google play activity
"""

import warnings
from pathlib import Path
from datetime import datetime
from typing import List, Any, Iterator
from urllib.parse import unquote
from itertools import chain

import lxml.html as lh
import pytz
from more_itertools import sliced

from .models import Metadata, HtmlEvent

from ..core.time import abbr_to_timezone

# Mar 8, 2018, 5:14:40 PM
_TIME_FORMAT = "%b %d, %Y, %I:%M:%S %p"


# ugh. something is seriously wrong with datetime, it wouldn't parse timezone aware UTC timestamp :(
def parse_dt(s: str) -> datetime:
    fmt = _TIME_FORMAT
    #
    # ugh. https://bugs.python.org/issue22377 %Z doesn't work properly

    end = s[-3:]
    tz: Any  # meh
    if end == " PM" or end == " AM":
        # old takeouts didn't have timezone
        # hopefully it was utc? Legacy, so no that much of an issue anymore..
        tz = pytz.utc
    else:
        s, tzabbr = s.rsplit(maxsplit=1)
        tz = abbr_to_timezone(tzabbr)

    dt = datetime.strptime(s, fmt)
    dt = tz.localize(dt)
    return dt


def test_parse_dt():
    parse_dt("Jun 23, 2015, 2:43:45 PM")
    parse_dt("Jan 25, 2019, 8:23:48 AM GMT")
    parse_dt("Jan 22, 2020, 8:34:00 PM UTC")
    parse_dt("Sep 10, 2019, 8:51:45 PM MSK")


def get_hrefs(el: lh.HtmlElement) -> Iterator[str]:
    for a in el.findall("a"):
        for k, v in a.items():
            if k == "href":
                yield v


def clean_latin1_chars(s: str):
    return s.replace("\xa0", "").replace("\u2003", "")


def itertext_range(el: lh.HtmlElement) -> Iterator[str]:
    # \xa0 is latin1 encoded space
    yield from map(clean_latin1_chars, el.itertext())


def itertext(el: lh.HtmlElement) -> str:
    return " ".join(list(itertext_range(el)))


def parse_div(div: lh.HtmlElement):
    title = div.cssselect("p.mdl-typography--title")[0].text_content()
    # remove text-right items, they're blank and for spaces
    content_cells: List[lh.HtmlElement] = list(
        filter(
            lambda d: "mdl-typography--text-right" not in d.classes,
            div.cssselect(".content-cell"),
        )
    )
    if len(content_cells) != 2:
        return RuntimeError(
            "Expected 2 content divs while parsing, found {}: {}".format(
                len(content_cells), div.text_content()
            )
        )
    # describes what the action is, last item here is the date
    content_description: List[str] = list(itertext_range(content_cells[0]))
    # parse date
    date = None
    if len(content_description) > 1:
        date = parse_dt(content_description.pop())
    else:
        warnings.warn(
            f"Didn't extract more than one text node from {title} {itertext(content_cells[0])}"
        )
    content_desc: str = " ".join(content_description)

    # split into key-value pairs of product: productname, Location: location etc.
    captions: List[Metadata] = [tuple(key_val) for key_val in sliced(list(itertext_range(content_cells[1])), 2)]  # type: ignore
    # note mypy cant coerce it into elements of two even though its slicing

    # iterate all links
    content_links: List[str] = [
        unquote(ainfo[2])
        for ainfo in chain(*map(lambda el: el.iterlinks(), content_cells))
    ]

    return HtmlEvent(
        service=title,
        desc=content_desc,
        metadata=captions,
        links=content_links,
        at=date,
    )


def read_html(p: Path):
    # this is gonna be cached behind cachew anyways
    doc = lh.fromstring(p.read_text())
    for outer_div in doc.cssselect("div.outer-cell"):
        yield parse_div(outer_div)
