import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Iterator

from .models import HtmlEventLinks


# doesnt have extra links like 'My Activity', doesn't need to have 'links'
def read_youtube_json_history(p: Path) -> Iterator[HtmlEventLinks]:
    for blob in json.loads(p.read_text()):
        links = []
        if "titleUrl" in blob:
            links.append(blob["titleUrl"])
        yield HtmlEventLinks(
            service="Youtube",
            product_name="Youtube",
            desc=blob["title"],
            dt=_parse_utc_date(blob["time"]),
            links=json.dumps(links),
        )


def _parse_utc_date(date_string: str) -> datetime:
    ds = date_string.rstrip("Z")
    return datetime.astimezone(datetime.fromisoformat(ds), tz=timezone.utc)
