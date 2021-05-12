from datetime import datetime
from typing import NamedTuple, Union, Iterator


class Event(NamedTuple):
    event_type: str
    dt: datetime
    channel: str
    # e.g., additional data/chatlog message
    context: Union[str, int]


Results = Iterator[Event]
