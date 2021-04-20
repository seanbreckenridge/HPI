"""
Parses the apple GPDR Export
"""

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import apple as user_config  # type: ignore[attr-defined]
from my.core import PathIsh, dataclass


@dataclass
class config(user_config):
    # path to unpacked GDPR archive
    gdpr_dir: PathIsh


import os
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Dict, Any, NamedTuple, Union, Optional

from lxml import etree  # type: ignore[import]
from more_itertools import sliced, first

from my.core import Stats, Res, LazyLogger
from my.core.common import mcachew


logger = LazyLogger(__name__, level="warning")


class Game(NamedTuple):
    name: str
    last_played: datetime


# some duplication here to allow cachew usage
class GameLeaderboardData(NamedTuple):
    game_name: str
    title: str
    dt: datetime
    rank: int


class GameAchievement(NamedTuple):
    dt: datetime
    percentage: int
    game_name: str
    title: str

    @property
    def achieved(self) -> bool:
        return self.percentage == 100


class Location(NamedTuple):
    lng: float
    lat: float
    dt: datetime
    name: str
    address: Optional[str]


Event = Union[
    Game,
    GameLeaderboardData,
    GameAchievement,
    Location,
]

Results = Iterator[Res[Event]]


@mcachew(
    depends_on=lambda: sorted(Path(config.gdpr_dir).expanduser().rglob("*")),
    logger=logger,
)
def events() -> Results:
    gdpr_dir = Path(config.gdpr_dir).expanduser().absolute()  # expand path
    handler_map = {
        "Apple ID account and device information": None,
        "Apple Online and Retail Stores": None,
        "iCloud Bookmarks": None,  # TODO: parse,
        "Wallet Activity": None,
        "Game Center/Game Center Data.json": _parse_game_center,
        "iCloud Notes": None,  # TODO: parse/copy?
        "Marketing communications": None,
        "iCloud Contacts": None,
        "iCloud Calendars and Reminders": None,  # TODO: parse
        "Other data/Apple Features Using iCloud/EventKit/Locations.xml": _parse_locations,
        "Other data/Apple Features Using iCloud/Calendar/": _parse_calendar_recents,
        "Other data/Apple Features Using iCloud/Mail": None,  # probably better to just do an IMAP sync and get all the data
        "Other data/": None,  # ignore anything else in this directory
    }
    for f in gdpr_dir.rglob("*"):
        handler: Any
        for prefix, h in handler_map.items():
            if not str(f).startswith(os.path.join(gdpr_dir, prefix)):
                continue
            handler = h
            break
        else:
            if f.is_dir():
                # rglob("*") matches directories, ignore those
                continue
            else:
                e = RuntimeError(f"Unhandled file: {f}")
                logger.debug(str(e))
                yield e
                continue

        if handler is None:
            # explicitly ignored
            continue

        yield from handler(f)


def stats() -> Stats:
    from my.core import stat

    return {
        **stat(events),
    }


def _parse_game_center(
    f: Path,
) -> Iterator[Union[Game, GameLeaderboardData, GameAchievement]]:
    for gme in json.loads(f.read_text())["games_state"]:
        yield Game(
            name=gme["game_name"],
            last_played=_parse_apple_utc_date(gme["last_played_utc"]),
        )
        for lb_inf in gme["leaderboard"]:
            for lb_val in lb_inf["leaderboard_score"]:
                yield GameLeaderboardData(
                    game_name=gme["game_name"],
                    title=lb_inf["leaderboard_title"],
                    rank=lb_val["rank"],
                    dt=_parse_apple_utc_date(lb_val["submitted_time_utc"]),
                )
        for ach_info in gme["achievements"]:
            yield GameAchievement(
                dt=_parse_apple_utc_date(ach_info["last_update_utc"]),
                game_name=gme["game_name"],
                percentage=ach_info["percentage_complete"],
                title=ach_info["achievements_title"],
            )


def _parse_locations(f: Path) -> Iterator[Location]:
    tr = etree.parse(str(f))
    for location in _parse_apple_xml_val(tr.find("array")):
        loc_data: Dict[str, Any] = first(list(location.values()))
        if "t" in loc_data:
            for tstamp in loc_data["t"]:
                yield Location(
                    lng=loc_data["map location"]["longitude"],
                    lat=loc_data["map location"]["latitude"],
                    name=loc_data["display name"],
                    address=loc_data["address"],
                    dt=tstamp,
                )


def _parse_calendar_recents(f: Path) -> Iterator[Location]:
    tr = etree.parse(str(f))
    for location in _parse_apple_xml_val(tr.find("array")):
        loc_data: Dict[str, Any] = first(list(location.values()))
        if "map location" in loc_data:
            if "t" in loc_data:
                for tstamp in loc_data["t"]:
                    yield Location(
                        lng=loc_data["map location"]["longitude"],
                        lat=loc_data["map location"]["latitude"],
                        name=loc_data["display name"],
                        address=first(loc_data.get("addressArray", []), None),
                        dt=tstamp,
                    )


# parses apples XML file format, specifies what should be JSON as XML
def _parse_apple_xml_val(xml_el):
    if xml_el.tag == "array":
        return [_parse_apple_xml_val(el) for el in xml_el]
    elif xml_el.tag == "dict":
        return {
            key.text: _parse_apple_xml_val(val) for key, val in sliced(list(xml_el), 2)
        }
    elif xml_el.tag == "string":
        return xml_el.text
    elif xml_el.tag == "integer":
        return int(xml_el.text)
    elif xml_el.tag == "real":
        return float(xml_el.text)
    elif xml_el.tag == "date":
        # is this UTC? probably, since others are
        return datetime.astimezone(
            datetime.fromisoformat(xml_el.text.rstrip("Z")), tz=timezone.utc
        )
    elif xml_el.tag == "data":
        return xml_el.text  # BASE64 data, dont think I need this
    else:
        raise RuntimeError(f"Unknown tag: {xml_el.tag}")


def _parse_apple_utc_date(dstr: str) -> datetime:
    return datetime.astimezone(
        datetime.strptime(dstr.rstrip("Z"), r"%m/%d/%Y %H:%M:%S"), tz=timezone.utc
    )
