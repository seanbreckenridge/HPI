"""
Parses the linkedin privacy/export
https://www.linkedin.com/help/linkedin/answer/50191/downloading-your-account-data?lang=en
"""

REQUIRES = ["dateparser"]

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import linkedin as user_config  # type: ignore[attr-defined]

from my.core import PathIsh, dataclass


@dataclass
class config(user_config.privacy_export):
    # path to unpacked privacy export, or a zip
    gdpr_dir: PathIsh


import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Dict, cast, Optional
from io import StringIO

import dateparser

from my.core import Stats, make_logger
from my.core.structure import match_structure


logger = make_logger(__name__)


EXPECTED = (
    "Registration.csv",
    "messages.csv",
    "Jobs",
    "Profile.csv",
)


def input() -> Path:
    return Path(config.gdpr_dir).expanduser().absolute()


DATELIKE_KEYS = {"date", "time"}
ENDSWITH_KEYS = {" on", " at"}


def _dateparser_to_utc(val: str) -> Optional[datetime]:
    dt_data = dateparser.parse(val)
    if dt_data is not None:
        return datetime.fromtimestamp(dt_data.timestamp(), tz=timezone.utc)
    return None


@dataclass
class Event:
    data: Dict[str, str]
    event_type: str  # file name this was read from

    def iter_dts(self) -> Iterator[datetime]:
        for k, v in self.data.items():
            kl = k.lower()
            for en in ENDSWITH_KEYS:
                if kl.endswith(en):
                    data = _dateparser_to_utc(v)
                    if data is not None:
                        yield data
            for dk in DATELIKE_KEYS:
                if dk in kl:
                    data = _dateparser_to_utc(v)
                    if data is not None:
                        yield data

    @property
    def dt(self) -> Optional[datetime]:
        """Try to parse a datetime from this event"""
        if hasattr(self, "_dt"):
            return cast(datetime, getattr(self, "_dt"))
        dts = list(set(self.iter_dts()))
        if len(dts) >= 1:
            if len(dts) >= 2:
                logger.debug(f"Parsed multiple dates from {self.data}: {dts}")
            setattr(self, "_dt", dts[0])
            return dts[0]
        return None


Results = Iterator[Event]


def events() -> Iterator[Event]:
    with match_structure(input(), expected=EXPECTED, partial=True) as exports:
        for exp in exports:
            for csv_file in exp.rglob("*"):
                if not csv_file.is_file():
                    continue
                yield from _csv_to_json(csv_file)


# TODO: cache?
def connections() -> Iterator[Event]:
    yield from filter(lambda f: f.event_type == "connections", events())


def _csv_to_json(p: Path) -> Iterator[Event]:
    event_type = p.stem.strip().casefold().replace(" ", "_")
    text = p.read_text()
    # some items have 'Notes:' at the top, which are useless when parsing
    if text.startswith("Notes:\n"):
        # hopefully this is robust enough? -- seems to always be nother line after the note
        if "\n\n" in text.strip():
            text = text.split("\n\n", maxsplit=1)[1]
    reader = csv.reader(StringIO(text))
    header = next(reader)
    header_mapping = {i: t for i, t in enumerate(header)}
    for line in reader:
        # ignore empty lines -- not sure why they're present sometimes
        if "".join(line).strip() == "":
            continue
        yield Event(
            event_type=event_type,
            data={header_mapping[i]: line[i] for i in header_mapping},
        )


def stats() -> Stats:
    from my.core import stat

    return {
        **stat(events),
        **stat(connections),
    }
