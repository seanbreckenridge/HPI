"""
Parses league of legend history from my `lolexport.parse` format
from: https://github.com/seanbreckenridge/lolexport
"""

REQUIRES = ["git+https://github.com/seanbreckenridge/lolexport"]


# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import league as user_config  # type: ignore[attr-defined]
from my.core import Paths, dataclass


@dataclass
class config(user_config.export):
    # path[s]/glob to the exported data. These are the resulting json file from 'lolexport parse'
    export_path: Paths

    # leauge of legends username
    username: str


import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import NamedTuple, Iterator, Sequence, Dict, Union, List, Optional, Set
from functools import partial
from itertools import chain

from my.core import get_files, Stats, Res, Json, warn_if_empty
from my.utils.time import parse_datetime_millis
from my.utils.input_source import InputSource


def inputs() -> Sequence[Path]:
    """
    Get the parsed league of legends JSON files
    (output of https://github.com/seanbreckenridge/lolexport/blob/master/lolexport/parse.py)
    """
    return get_files(config.export_path)


ChampionInfo = Dict[str, Union[str, List[str]]]
Metadata = Optional[str]
Names = List[str]

# represents one League of Legends game
class Game(NamedTuple):
    champion_name: str
    game_id: int
    season: int
    game_started: datetime
    game_duration: timedelta
    players: Names
    my_stats: Json  # just my characters' stats, though all are in the JSON dump
    all_stats: List[Json]
    queue: Optional[Dict[str, str]]
    role: Metadata
    lane: Metadata
    map_name: Metadata
    game_mode: Metadata
    game_type: Metadata

    @property
    def won(self) -> bool:
        won = self.my_stats["win"]
        assert isinstance(won, bool)
        return won

    @property
    def champions(self) -> Names:
        return [str(s["champion"]["name"]) for s in self.all_stats]

    @property
    def game_ended(self) -> datetime:
        return self.game_started + self.game_duration


Results = Iterator[Res[Game]]


def history(
    from_paths: InputSource = inputs, summoner_name: Optional[str] = None
) -> Results:
    sname: Optional[str] = summoner_name or config.username
    if sname is None:
        raise RuntimeError("No league of legends username received!")
    _json_for_user = partial(_read_parsed_json, username=sname)
    yield from _merge_histories(*map(_json_for_user, from_paths()))


@warn_if_empty
def _merge_histories(*sources: Results) -> Results:
    emitted: Set[int] = set()
    for g in chain(*sources):
        if isinstance(g, Exception):
            yield g
        else:
            if g.game_id in emitted:
                continue
            emitted.add(g.game_id)
            yield g


def _read_parsed_json(p: Path, username: str) -> Results:
    items = json.loads(p.read_text())
    for game in items:
        playerNames: Dict[int, str] = {
            int(uid): name for uid, name in game["playerNames"].items()
        }
        # get my participant_id from the playerNames
        try:
            participant_id: int = next(
                (k for k, v in playerNames.items() if v == username)
            )
        except StopIteration:
            yield RuntimeError(f"Couldn't extract id for {username} from {playerNames}")
            continue
        # get my stats
        try:
            my_stats = next(
                filter(
                    lambda ustats: int(ustats["participantId"]) == participant_id,
                    game["stats"],
                )
            )
        except StopIteration:
            yield RuntimeError(f"Couldn't extract stats for game {game['gameId']}")
            continue
        else:
            # if try try block didn't error, use my_stats
            # assuming datetime is epoch ms
            yield Game(
                champion_name=game["champion"]["name"],
                game_id=game["gameId"],
                queue=game.get("queue"),
                season=game.get("season"),
                role=_remove_none(game.get("role")),
                lane=_remove_none(game.get("lane")),
                game_started=parse_datetime_millis(game["gameCreation"]),
                game_duration=timedelta(seconds=game["gameDuration"]),
                map_name=game["map"],
                game_mode=game["gameMode"],
                game_type=game["gameType"],
                players=list(playerNames.values()),
                my_stats=my_stats,
                all_stats=game["stats"],
            )


# convert the 'NONE' string to a None object
def _remove_none(m: Optional[str]) -> Optional[str]:
    if m is not None and m.upper() == "NONE":
        return None
    return m


def stats() -> Stats:
    from my.core import stat

    return {**stat(history)}
