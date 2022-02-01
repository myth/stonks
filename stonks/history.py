from asyncio import sleep
from datetime import datetime, time, timedelta
from logging import getLogger
from typing import Any, Dict, List

from . import config as c
from .events import EventType
from .task import Task

LOG = getLogger(__name__)


class CandleStick:
    def __init__(self, _time: datetime, _open: int, _high: int, _low: int, _close: int):
        def vt(f, t, n):
            if not isinstance(f, t):
                raise TypeError(f"Argument '{n}' must be type {t}, got {type(f)}")

        vt(_time, datetime, "_time")
        vt(_open, int, "_open")
        vt(_high, int, "_high")
        vt(_low, int, "_low")
        vt(_close, int, "_close")

        self.time = _time
        self.open = _open
        self.high = _high
        self.low = _low
        self.close = _close

    def tick(self, nav: int) -> None:
        self.close = nav
        if nav > self.high:
            self.high = nav
        elif nav < self.low:
            self.low = nav

    def next(self) -> "CandleStick":
        t = self.time + timedelta(hours=1)
        return CandleStick(t, self.close, self.close, self.close, self.close)

    def json(self) -> Dict[str, Any]:
        return {
            "time": int(self.time.timestamp()),
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
        }

    @classmethod
    def create(cls, nav: int):
        target = datetime.now(c.TZ) + timedelta(hours=1)
        t = datetime.combine(target.date(), time(target.hour), c.TZ)
        return cls(t, nav, nav, nav, nav)

    @classmethod
    def create_from_db(cls, _time: int, *args):
        return cls(datetime.fromtimestamp(_time, c.TZ), *args)

    def __repr__(self):
        return f"CandleStick<{self.time}>[open={self.open} high={self.high} low={self.low} close={self.close}]"


class History(Task):
    def __init__(self) -> None:
        super().__init__("Portfolio history")
        self.history: List[CandleStick] = []
        self.active = None

    def set_history(self, history: List[CandleStick]):
        self.history = history[-c.HISTORY_BUFFER:]
        if self.history:
            self.active = CandleStick.create(self.history[-1].close)
            LOG.info("[%s] Initialized active candlestick from history %s", self.name, self.active)

    async def tick(self, nav: int):
        if self.active:
            self.active.tick(nav)
        else:
            self.active = CandleStick.create(nav)
            self.history.append(self.active)
            LOG.info("[%s] Initialized first candlestick %s", self.name, self.active)

        await self.emit(EventType.CHART_TICK, self.active.json())

    async def close(self):
        if not self.active:
            return

        await self.emit(EventType.CLOSE, self.active)
        self.active = self.active.next()
        self.history.append(self.active)

        if len(self.history) > c.HISTORY_BUFFER:
            self.history = self.history[-c.HISTORY_BUFFER:]

    async def run(self):
        self.running = True

        while self.running:
            if self.active:
                target = self.active.time
            else:
                target = datetime.now(c.TZ) + timedelta(hours=1)
                target = datetime.combine(target.date(), time(target.hour), c.TZ)
            wait = target - datetime.now(c.TZ)

            LOG.debug("[%s] Waiting %s until next close", self.name, wait)
            await sleep(wait.total_seconds())

            self.close()
            await self.emit(EventType.CHART, self.json())

    async def stop(self):
        LOG.info("[%s] Stopping...", self.name)
        self.restart = False
        self.running = False
        LOG.info("[%s] Stopped", self.name)

    def json(self):
        return [c.json() for c in self.history]

    def __len__(self) -> int:
        return len(self.history)