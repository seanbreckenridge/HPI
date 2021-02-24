"""
Parses league of legend history from my `lolexport.parse` format
from: https://github.com/seanbreckenridge/lolexport
"""

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import league_of_legends as user_config

from dataclasses import dataclass

from ..core import Paths


@dataclass
class league_of_legends(user_config):
    # path[s]/glob to the exported data. These are the resulting json file from 'lolexport parse'
    export_path: Paths

    # leauge of legends username
    username: str


from ..core.cfg import make_config

config = make_config(league_of_legends)

#######

import json
from pathlib import Path
from datetime import datetime
from typing import NamedTuple, Iterator, Sequence, Dict, Union, List, Optional, Any, Set
from functools import partial
from itertools import chain

from ..core import get_files, Stats
from ..core.error import Res
from ..core.time import parse_datetime_millis


def inputs() -> Sequence[Path]:
    """
    Get the parsed league of legends JSON files
    (output of https://github.com/seanbreckenridge/lolexport/blob/master/lolexport/parse.py)
    """
    return get_files(config.export_path)


ChampionInfo = Dict[str, Union[str, List[str]]]
Metadata = Optional[str]
Json = Dict[str, Any]
Players = List[str]

# represents one League of Legends game
class Game(NamedTuple):
    champion_name: str
    game_id: int
    season: int
    game_creation: datetime
    game_duration: int
    players: Players
    my_stats: Json  # just my characters' stats, though all are in the JSON dump
    all_stats: List[Json]
    queue: Metadata
    role: Metadata
    lane: Metadata
    map_name: Metadata
    game_mode: Metadata
    game_type: Metadata

    @property
    def won(self):
        return self.my_stats["win"]

    @property
    def champions(self):
        return map(lambda s: s["champion"]["name"], self.all_stats)


Results = Iterator[Res[Game]]


def history(from_paths=inputs, summoner_name: Optional[str] = None) -> Results:
    if summoner_name is None:
        if config.username is None:
            raise RuntimeError("No league of legends username received!")
        else:
            summoner_name = config.username
    _read_parsed_json_for_user = partial(_read_parsed_json, username=summoner_name)
    yield from _merge_histories(*map(_read_parsed_json_for_user, from_paths()))

def _merge_histories(*sources: Results) -> Results:
    emitted: Set[int] = set()
    for g in chain(*sources):
        if g.game_id in emitted:
            continue
        yield g
        emitted.add(g.game_id)



def _read_parsed_json(p: Path, username: str) -> Results:
    items = json.loads(p.read_text())
    for game in items:
        # get my stats
        participant_id = [k for k, v in game["playerNames"].items() if v == username]
        if len(participant_id) != 1:
            yield RuntimeError(
                f"Couldn't extract id for {username} from {game['playerNames']}"
            )
        else:
            my_stats = list(
                filter(
                    lambda user_stats: int(user_stats["participantId"])
                    == int(participant_id[0]),
                    game["stats"],
                )
            )[0]
            # assuming datetime is epoch ms
            yield Game(
                champion_name=game["champion"]["name"],
                game_id=game["gameId"],
                queue=game.get("queue"),
                season=game.get("season"),
                role=game.get("role"),
                lane=game.get("lane"),
                game_creation=parse_datetime_millis(game["gameCreation"]),
                game_duration=game["gameDuration"],
                map_name=game["map"],
                game_mode=game["gameMode"],
                game_type=game["gameType"],
                players=list(game["playerNames"].values()),
                my_stats=my_stats,
                all_stats=game["stats"],
            )


def stats() -> Stats:
    from ..core import stat

    return {**stat(history)}
