from datetime import datetime
from typing import List, NamedTuple, Tuple

Metadata = Tuple[str, str]  # key-value pair from html caption


# need to do some analysis on the metadata/links once its all parsed
# to see if it can be simplified into an ADT which doesnt have
# variant lists
class HtmlEvent(NamedTuple):
    service: str
    desc: str
    metadata: List[Metadata]
    links: List[str]
    at: datetime
