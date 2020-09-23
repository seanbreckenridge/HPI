from datetime import datetime
from typing import List, NamedTuple, Tuple, Optional

Metadata = Tuple[str, str]  # key-value pair from html caption


class HtmlEvent(NamedTuple):
    service: str
    desc: str
    metadata: List[Metadata]
    links: List[str]
    at: Optional[datetime]
