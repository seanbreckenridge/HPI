"""
Extracts metadata from the automatic runelite (OldSchool RuneScape Client) screenshots
that happen when you finish quests/gain levels
https://github.com/runelite/runelite/wiki/Screenshot
"""

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import runelite as user_config  # type: ignore[attr-defined]

from my.core import Paths, dataclass


@dataclass
class config(user_config.screenshots):
    # path[s]/glob to the base screenshot directory or each username
    # this can be some rsynced folder (like my jobs/computer/runelite_screenshots.job does)
    # or the .runelite folder itself
    export_path: Paths


import re
from pathlib import Path
from typing import Sequence, Union, NamedTuple, Iterator, Tuple
from datetime import datetime

from my.core import get_files, Stats
from my.core.structure import match_structure
from my.utils.input_source import InputSource

EXPECTED = ("Levels", "Quests")


def accounts() -> Sequence[Path]:
    accounts = []
    for f in get_files(config.export_path):
        with match_structure(f, EXPECTED) as match:
            accounts.extend(list(match))
    return accounts


class Level(NamedTuple):
    skill: str
    level: int


Description = Union[Level, str]


class Screenshot(NamedTuple):
    """represents one screenshot (quest/level etc.)"""

    dt: datetime
    path: Path
    screenshot_type: str  # Level/Quest etc
    description: Description
    username: str


Results = Iterator[Screenshot]


def screenshots(for_accounts: InputSource = accounts) -> Results:
    for account in for_accounts():
        for p in account.iterdir():
            if p.is_dir():
                yield from _parse_subdir(p, username=account.stem)


DT_REGEX = r"%Y-%m-%d_%H-%M-%S"

# TODO: use tz module to optionally figure out what timezone I was
# when the file was created, so I can make sure the info in the filename
# being a naive date isn't an issue if I'm ever in another timezone


def _extract_info_from_filename(p: Path) -> Tuple[str, datetime]:
    desc, _, dstr = p.stem.rpartition(" ")
    return desc.strip(), datetime.strptime(dstr, DT_REGEX)


def _parse_subdir(p: Path, username: str) -> Results:
    if p.stem == "Levels":
        yield from _parse_level_dir(p, username=username)
    elif p.stem == "Quests":
        yield from _parse_quest_dir(p, username=username)
    else:
        yield from _parse_other_dir(p, username=username)


QUEST_REGEX = re.compile(r"^Quest\((.*?)\)$")


def _parse_quest_dir(p: Path, username: str) -> Results:
    for img in p.rglob("*.png"):
        desc, dt = _extract_info_from_filename(img)
        m = re.match(QUEST_REGEX, desc)
        assert m, f"Couldn't extract quest name from {desc}"
        yield Screenshot(
            dt=dt,
            path=img,
            screenshot_type="Quest",
            description=m.group(1),
            username=username,
        )


LEVEL_REGEX = re.compile(r"^([\w ]+)\((\d+)\)$")


def _parse_level_dir(p: Path, username: str) -> Results:
    for img in p.rglob("*.png"):
        desc, dt = _extract_info_from_filename(img)
        m = re.match(LEVEL_REGEX, desc)
        assert m, f"Could not match levels out of {desc}"
        skill_name, level = m.groups()
        yield Screenshot(
            dt=dt,
            path=img,
            screenshot_type="Level",
            description=Level(skill=skill_name, level=int(level)),
            username=username,
        )


def _parse_other_dir(p: Path, username: str) -> Results:
    for img in p.rglob("*.png"):
        desc, dt = _extract_info_from_filename(img)
        yield Screenshot(
            dt=dt, path=img, screenshot_type=p.stem, description=desc, username=username
        )


def stats() -> Stats:
    from my.core import stat

    return {**stat(screenshots)}
