"""
Reddit data: saved items/comments/upvotes/etc.
"""
REQUIRES = [
    "git+https://github.com/karlicoss/rexport",
]

import os
from .core.common import Paths

from my.config import reddit as uconfig
from dataclasses import dataclass


@dataclass
class reddit(uconfig):
    """
    Uses [[https://github.com/karlicoss/rexport][rexport]] output.
    """

    # path[s]/glob to the exported JSON data
    export_path: Paths

    # path to one or more https://github.com/seanbreckenridge/pushshift_comment_export exported data
    pushshift_export_path: Paths


from .core.cfg import make_config, Attrs

# hmm, also nice thing about this is that migration is possible to test without the rest of the config?
def migration(attrs: Attrs) -> Attrs:
    export_dir = "export_dir"
    if export_dir in attrs:  # legacy name
        attrs["export_path"] = attrs[export_dir]
        from .core.warnings import high

        high(f'"{export_dir}" is deprecated! Please use "export_path" instead."')
    return attrs


config = make_config(reddit, migration=migration)

try:
    from rexport import dal

    # monkey patch with HPI_LOGS
    dal.get_logger = lambda: dal.logging_helper.LazyLogger(
        "rexport", level=os.environ.get("HPI_LOGS", "WARNING")
    )
except ModuleNotFoundError as e:
    from .core.compat import pre_pip_dal_handler

    dal = pre_pip_dal_handler("rexport", e, config, requires=REQUIRES)

############################

from typing import List, Sequence, Mapping, Iterator, Union
from .core.common import mcachew, get_files, LazyLogger, make_dict, warn_if_empty, Stats

# comments further back than what the reddit API (1000 results) can get
# https://github.com/seanbreckenridge/pushshift_comment_export
from pushshift_comment_export.dal import PComment, read_file

RComment = Union[PComment, dal.Comment]


logger = LazyLogger(__name__, level="debug")


from pathlib import Path


def inputs() -> Sequence[Path]:
    return get_files(config.export_path)


Sid = str
Save = dal.Save
Comment = dal.Comment
Submission = dal.Submission
Upvote = dal.Upvote


def _dal() -> dal.DAL:
    inp = list(inputs())
    return dal.DAL(inp)


cache = mcachew(
    depends_on=lambda: list(inputs()).extend(list(comment_inputs()))
)  # depends on inputs only


@cache
def saved() -> Iterator[Save]:
    return _dal().saved()


@cache
def comments() -> Iterator[RComment]:
    # prefer _dal.comments to pushshift, gets added to emitted first
    yield from _merge_comments(_dal().comments(), pushshift_comments())


@cache
def submissions() -> Iterator[Submission]:
    return _dal().submissions()


@cache
def upvoted() -> Iterator[Upvote]:
    return _dal().upvoted()


### the rest of the file is some elaborate attempt of restoring favorite/unfavorite times

from typing import Dict, Union, Iterable, Iterator, NamedTuple
from functools import lru_cache
import pytz
import re
from datetime import datetime
from multiprocessing import Pool

# TODO hmm. apparently decompressing takes quite a bit of time...


class SaveWithDt(NamedTuple):
    save: Save
    backup_dt: datetime

    def __getattr__(self, x):
        return getattr(self.save, x)


# TODO for future events?
EventKind = SaveWithDt


class Event(NamedTuple):
    dt: datetime
    text: str
    kind: EventKind
    eid: str
    title: str
    url: str

    @property
    def cmp_key(self):
        return (self.dt, (1 if "unfavorited" in self.text else 0))


Url = str


def _get_bdate(bfile: Path) -> datetime:
    RE = re.compile(r"(\d{14})")
    stem = bfile.stem
    stem = stem.replace("T", "").replace("Z", "")  # adapt for arctee
    match = RE.search(stem)
    assert match is not None
    bdt = pytz.utc.localize(datetime.strptime(match.group(1), "%Y%m%d%H%M%S"))
    return bdt


def _get_state(bfile: Path) -> Dict[Sid, SaveWithDt]:
    logger.debug("handling %s", bfile)

    bdt = _get_bdate(bfile)

    saves = [SaveWithDt(save, bdt) for save in dal.DAL([bfile]).saved()]
    return make_dict(
        sorted(saves, key=lambda p: p.save.created),
        key=lambda s: s.save.sid,
    )


# TODO hmm. think about it.. if we set default backups=inputs()
# it's called early so it ends up as a global variable that we can't monkey patch easily
@mcachew
def _get_events(backups: Sequence[Path], parallel: bool = True) -> Iterator[Event]:
    # TODO cachew: let it transform return type? so you don't have to write a wrapper for lists?

    prev_saves: Mapping[Sid, SaveWithDt] = {}
    # TODO suppress first batch??
    # TODO for initial batch, treat event time as creation time

    states: Iterable[Mapping[Sid, SaveWithDt]]
    if parallel:
        with Pool() as p:
            states = p.map(_get_state, backups)
    else:
        # also make it lazy...
        states = map(_get_state, backups)
    # TODO mm, need to make that iterative too?

    for i, (bfile, saves) in enumerate(zip(backups, states)):
        bdt = _get_bdate(bfile)

        first = i == 0

        for key in set(prev_saves.keys()).symmetric_difference(set(saves.keys())):
            ps = prev_saves.get(key, None)
            if ps is not None:
                # TODO use backup date, that is more precise...
                # eh. I guess just take max and it will always be correct?
                assert not first
                yield Event(
                    dt=bdt,  # TODO average wit ps.save_dt?
                    text="unfavorited",
                    kind=ps,
                    eid=f"unf-{ps.sid}",
                    url=ps.url,
                    title=ps.title,
                )
            else:  # already in saves
                s = saves[key]
                last_saved = s.backup_dt
                yield Event(
                    dt=s.created if first else last_saved,
                    text="favorited{}".format(" [initial]" if first else ""),
                    kind=s,
                    eid=f"fav-{s.sid}",
                    url=s.url,
                    title=s.title,
                )
        prev_saves = saves

    # TODO a bit awkward, favorited should compare lower than unfavorited?


@lru_cache(1)
def events(*args, **kwargs) -> List[Event]:
    inp = inputs()
    # 2.2s for 300 files without cachew
    # 0.2s for 300 files with cachew
    evit = _get_events(inp, *args, **kwargs, parallel=False)
    return list(sorted(evit, key=lambda e: e.cmp_key))


def stats() -> Stats:
    from .core import stat

    return {
        **stat(saved),
        **stat(comments),
        **stat(submissions),
        **stat(upvoted),
    }


def main() -> None:
    for e in events(parallel=False):
        print(e)


if __name__ == "__main__":
    main()

# load in additional comments from pushshift

from itertools import chain
from typing import Set, Union


def comment_inputs() -> Sequence[Path]:
    return get_files(config.pushshift_export_path)


def pushshift_comments() -> Iterator[PComment]:
    return chain(*map(read_file, comment_inputs()))


# combine comments
# not going to be totally compatible, because rexport and
# pushshift have different JSON representations. Looks like
# a lot of the major ones are the same though
@warn_if_empty
def _merge_comments(*sources: Sequence[RComment]) -> Iterator[RComment]:
    ignored = 0
    emitted: Set[int] = set()
    for e in chain(*sources):
        key = int(e.raw["created_utc"])
        if key in emitted:
            ignored += 1
            # logger.info('ignoring %s: %s', key, e)
            continue
        yield e
        emitted.add(key)
    logger.info(f"Ignored {ignored} comments...")
    # tested 30/09/20
    # Ignoring 997...
