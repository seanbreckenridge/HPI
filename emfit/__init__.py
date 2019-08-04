#!/usr/bin/env python3
import json
import logging
from collections import OrderedDict as odict
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Dict, Iterator, List, NamedTuple

import kython
import pytz
from kython import cproperty, group_by_key

from cachew import cachew


def get_logger():
    return logging.getLogger('emfit-provider')

timed = lambda f: kython.timed(f, logger=get_logger())

def hhmm(minutes):
    return '{:02d}:{:02d}'.format(*divmod(minutes, 60))

PATH = Path("/L/backups/emfit")

EXCLUDED = [
    '***REMOVED***', # pretty weird, detected sleep and HR (!) during the day when I was at work
    '***REMOVED***',

    '***REMOVED***', # some weird sleep during the day?
]

AWAKE = 4

Sid = str

# TODO FIXME use tz provider for that? although emfit is always in london...
_TZ = pytz.timezone('Europe/London')

def fromts(ts) -> datetime:
    dt = datetime.fromtimestamp(ts)
    return _TZ.localize(dt)


class Mixin:
    @property
    # ok, I guess that's reasonable way of defining sleep date
    def date(self):
        return self.end.date()

    @cproperty
    def time_in_bed(self):
        return int((self.sleep_end - self.sleep_start).total_seconds()) // 60

    @property
    def recovery(self):
        return self.hrv_morning - self.hrv_evening

    @property
    def summary(self):
        return f"""in bed for {hhmm(self.time_in_bed)}
emfit time: {hhmm(self.sleep_minutes_emfit)}; covered: {self.sleep_hr_coverage:.0f}
hrv morning: {self.hrv_morning:.0f}
hrv evening: {self.hrv_evening:.0f}
avg hr: {self.measured_hr_avg:.0f}
recovery: {self.recovery:3.0f}
{self.hrv_lf}/{self.hrv_hf}"""


# TODO def use multiple threads for that..
class EmfitOld(Mixin):
    def __init__(self, sid: str, jj):
        self.sid = sid
        self.jj = jj

    def __hash__(self):
        return hash(self.sid)

    @property
    def hrv_morning(self):
        return self.jj['hrv_rmssd_morning']

    @property
    def hrv_evening(self):
        return self.jj['hrv_rmssd_evening']

    """
    Bed time, not necessarily sleep
    """
    @property
    def start(self):
        return fromts(self.jj['time_start'])

    """
    Bed time, not necessarily sleep
    """
    @property
    def end(self):
        return fromts(self.jj['time_end'])

    @property
    def epochs(self):
        return self.jj['sleep_epoch_datapoints']

    @property
    def epoch_series(self):
        tss = []
        eps = []
        for [ts, e] in self.epochs:
            tss.append(ts)
            eps.append(e)
        return tss, eps

    @cproperty
    def sleep_start(self) -> datetime:
        for [ts, e] in self.epochs:
            if e == AWAKE:
                continue
            return fromts(ts)
        raise RuntimeError

    @cproperty
    def sleep_end(self) -> datetime:
        for [ts, e] in reversed(self.epochs):
            if e == AWAKE:
                continue
            return fromts(ts)
        raise RuntimeError
# 'sleep_epoch_datapoints'
# [[timestamp, number]]

    # so it's actual sleep, without awake
    # ok, so I need time_asleep
    @property
    def sleep_minutes_emfit(self):
        return self.jj['sleep_duration'] // 60

    @property
    def hrv_lf(self):
        return self.jj['hrv_lf']

    @property
    def hrv_hf(self):
        return self.jj['hrv_hf']

    @property
    def strip_awakes(self):
        ff = None
        ll = None
        for i, [ts, e] in enumerate(self.epochs):
            if e != AWAKE:
                ff = i
                break
        for i in range(len(self.epochs) - 1, -1, -1):
            [ts, e] = self.epochs[i]
            if e != AWAKE:
                ll = i
                break
        return self.epochs[ff: ll]


    # # TODO epochs with implicit sleeps? not sure... e.g. night wakeups.
    # # I guess I could input intervals/correct data/exclude days manually?
    # @property
    # def pulse_percentage(self):

    #     # TODO pulse intervals are 4 seconds?
    #     # TODO ok, how to compute that?...
    #     # TODO cut ff start and end?
    #     # TODO remove awakes from both sides
    #     sp = self.strip_awakes
    #     present = {ep[0] for ep in sp}
    #     start = min(present)
    #     end = max(present)
    #     # TODO get start and end in one go?

    #     for p in self.iter_points():
    #         p.ts 


    #     INT = 30

    #     missing = 0
    #     total = 0
    #     for tt in range(start, end + INT, INT):
    #         total += 1
    #         if tt not in present:
    #             missing += 1
    #     # TODO get hr instead!
    #     import ipdb; ipdb.set_trace() 
    #     return missing


    #     st = st[0][0]
    #     INT = 30
    #     for [ts, e] in sp:
    #         if e == AWAKE:
    #             continue
    #         return fromts(ts)
    #     raise RuntimeError
    #     pass

    def __str__(self) -> str:
        return f"from {self.sleep_start} to {self.sleep_end}"

# measured_datapoints
# [[timestamp, pulse, breath?, ??? hrv?]] # every 4 seconds?

    def iter_points(self):
        for ll in self.jj['measured_datapoints']:
            [ts, pulse, br, activity] = ll
            # TODO what the fuck is whaat?? It can't be HRV, it's about 500 ms on average
            # act in csv.. so it must be activity? wonder how is it measured.
            # but I guess makes sense. yeah,  "measured_activity_avg": 595, about that
            # makes even more sense given tossturn datapoints only have timestamp
            yield ts, pulse

    @property
    def sleep_hr(self):
        tss = []
        res = []
        for ts, pulse in self.iter_points():
            if self.sleep_start < fromts(ts) < self.sleep_end:
                tss.append(ts)
                res.append(pulse)
        return tss, res

    @property
    def sleep_hr_series(self):
        return self.sleep_hr

    @property
    def hrv(self):
        tss = []
        res = []
        for ll in self.jj['hrv_rmssd_datapoints']:
            [ts, rmssd, _, _, almost_always_zero, _] = ll
            # timestamp,rmssd,tp,lfn,hfn,r_hrv
            # TP is total_power??
            # erm. looks like there is a discrepancy between csv and json data.
            # right, so web is using api v 1. what if i use v1??
            # definitely a discrepancy between v1 and v4. have no idea how to resolve it :(
            # also if one of them is indeed tp value, it must have been rounded.
            # TODO what is the meaning of the rest???
            # they don't look like HR data.
            tss.append(ts)
            res.append(rmssd)
        return tss, res

    @property
    def measured_hr_avg(self):
        return self.jj["measured_hr_avg"]

    @cproperty
    def sleep_hr_coverage(self):
        tss, hrs = self.sleep_hr
        covered = len([h for h in hrs if h is not None])
        expected = len(hrs)
        return covered / expected * 100


# right, so dataclass is better because you can use mixins
@dataclass(eq=True, frozen=True)
class Emfit(Mixin):
    sid: Sid
    hrv_morning: float
    hrv_evening: float
    start: datetime
    end  : datetime
    sleep_start: datetime
    sleep_end  : datetime
    sleep_hr_coverage: float
    measured_hr_avg: float
    sleep_minutes_emfit: int
    hrv_lf: float
    hrv_hf: float

    @classmethod
    def make(cls, em) -> Iterator['Emfit']:
        # TODO FIXME res?
        logger = get_logger()
        if em.epochs is None:
            logger.error('%s (on %s) got None in epochs! ignoring', em.sid, em.date)
            return

        yield cls(**{
            k: getattr(em, k) for k in Emfit.__annotations__
        })


# TODO move to common?
def dir_hash(path: Path):
    mtimes = tuple(p.stat().st_mtime for p in sorted(path.glob('*.json')))
    return mtimes


@cachew(db_path=Path('/L/data/.cache/emfit.cache'), hashf=dir_hash)
def iter_datas(path: Path) -> Iterator[Emfit]:
    for f in sorted(path.glob('*.json')):
        sid = f.stem
        if sid in EXCLUDED:
            continue

        em = EmfitOld(sid=sid, jj=json.loads(f.read_text()))
        yield from Emfit.make(em)


def get_datas() -> List[Emfit]:
    return list(sorted(iter_datas(PATH), key=lambda e: e.start))
# TODO move away old entries if there is a diff??


@timed
def by_night() -> Dict[date, Emfit]:
    logger = get_logger()
    res: Dict[date, Emfit] = odict()
    # TODO shit. I need some sort of interrupted sleep detection?
    for dd, sleeps in group_by_key(get_datas(), key=lambda s: s.date).items():
        if len(sleeps) > 1:
            logger.warning("multiple sleeps per night, not handled yet: %s", sleeps)
            continue
        [s] = sleeps
        res[s.date] = s
    return res



def test():
    datas = get_datas()
    for d in datas:
        assert len(d.epochs) > 0


def test_tz():
    datas = get_datas()
    for d in datas:
        assert d.start.tzinfo is not None
        assert d.end.tzinfo is not None
        assert d.sleep_start.tzinfo is not None
        assert d.sleep_end.tzinfo is not None

    # https://qs.emfit.com/#/device/presence/***REMOVED***
    # this was winter time, so GMT, UTC+0
    sid_20190109 = '***REMOVED***'
    [s0109] = [s for s in datas if s.sid == sid_20190109]
    assert s0109.end.time() == time(hour=6, minute=42)

    # summer time, so UTC+1
    sid_20190411 = '***REMOVED***'
    [s0411] = [s for s in datas if s.sid == sid_20190411]
    assert s0411.end.time() == time(hour=9, minute=30)


def main():
    from kython.klogging import setup_logzero
    setup_logzero(get_logger(), level=logging.DEBUG)
    for k, v in by_night().items():
        print(k, v.start, v.end)

if __name__ == '__main__':
    main()
