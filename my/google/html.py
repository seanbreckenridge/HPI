"""
Google Takeout exports: browsing history, search/youtube/google play activity
"""

import warnings
import re
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Any, Iterator, Optional
from urllib.parse import unquote
from itertools import chain

import lxml.html as lh
import pytz
from more_itertools import sliced

from .models import HtmlEvent, HtmlComment

from ..core.error import Res
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


def clean_latin1_chars(s: str):
    return s.replace("\xa0", "").replace("\u2003", "")


def itertext_range(el: lh.HtmlElement) -> Iterator[str]:
    # \xa0 is latin1 encoded space
    yield from map(clean_latin1_chars, el.itertext())


def itertext(el: lh.HtmlElement) -> str:
    return " ".join(list(map(str.strip, itertext_range(el))))


def get_links(el: lh.HtmlElement) -> List[str]:
    return [unquote(a_el[2]) for a_el in chain(*map(lambda e: e.iterlinks(), el))]


def parse_div(div: lh.HtmlElement) -> Res[HtmlEvent]:
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
    if len(content_description) > 1:
        try:
            date = parse_dt(content_description.pop())
        except Exception as e:
            return RuntimeError("Failure parsing date: {}".format(str(e)))
    else:
        warnings.warn(
            f"Didn't extract more than one text node from {title} {itertext(content_cells[0])}"
        )
    content_desc: str = " ".join(content_description)

    # TODO: parse this nicely? feels like this is good enough, especially behind cachew
    # split into key-value pairs of product: productname, Location: location etc.
    # just extract the product name
    kv_lists = list(sliced(list(itertext_range(content_cells[1])), 2))
    product_name: Optional[str] = None
    for kv in kv_lists:
        # should be a key, like Location:, Product
        # just grab the product name
        if len(kv) == 2:
            if "Products:" == kv[0]:
                product_name = kv[1].strip()
                break

    # iterate all links
    content_links: List[str] = list(chain(*map(get_links, content_cells)))

    return HtmlEvent(
        service=title,
        desc=content_desc,
        product_name=product_name,
        links=json.dumps(content_links),
        at=date,
    )


def read_html_activity(p: Path) -> Iterator[Res[HtmlEvent]]:
    # this is gonna be cached behind cachew anyways
    doc = lh.fromstring(p.read_text())
    for outer_div in doc.cssselect("div.outer-cell"):
        yield parse_div(outer_div)


# seems to always be in UTC?
COMMENT_DATE_REGEX = re.compile(
    r"([0-9]{4})\-([0-9]{2})\-([0-9]{2})\s*([0-9]{2})\:([0-9]{2})\:([0-9]{2})"
)

# for HtmlComment
# can be in lots of formats
# sent at '...'
# on '....'
# probably just need to use regex
def _extract_date(comment: str) -> Res[datetime]:
    matches = re.search(COMMENT_DATE_REGEX, comment)
    if matches:
        g = matches.groups()
        year, month, day, hour, minute, second = tuple(map(int, g))
        return datetime(year, month, day, hour, minute, second, tzinfo=timezone.utc)
    else:
        return RuntimeError("Couldn't parse date from {}".format(comment))


def read_html_li(p: Path) -> Iterator[Res[HtmlComment]]:
    doc = lh.fromstring(p.read_text())
    for li in doc.cssselect("li"):
        description: str = itertext(li)
        parsed_date: Res[datetime] = _extract_date(description)
        # TODO: remove the 'you added a comment on video' from prefix?
        if isinstance(parsed_date, Exception):
            yield parsed_date
        else:
            yield HtmlComment(
                desc=description, links=json.dumps(get_links(li)), at=parsed_date
            )
