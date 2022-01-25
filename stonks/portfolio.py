"""Portfolio"""

import asyncio
from asyncio.tasks import sleep
from collections import deque
from datetime import date, datetime, time, timedelta
from logging import getLogger
from json import load
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union


from . import config as c
from .db import DailyClose, Database
from .events import EventEmitter, EventType, Event
from .task import Task

LOG = getLogger(__name__)


class Forex:
    def __init__(self, name: str, ticker: str, market_price: float):
        self.name = name
        self.ticker = ticker
        self.market_price = market_price

    def json(self):
        return {
            "name": self.name,
            "ticker": self.ticker,
            "market_price": self.market_price,
            "asset": c.Asset.FOREX.value,
        }


class ExchangeRates(EventEmitter):
    def __init__(self):
        super().__init__()
        self.rates: Dict[str, Forex] = {f[0]: Forex(*f) for f in c.FOREX}
        self.rates_by_ticker: Dict[str, Forex] = {f.ticker: f for f in self.rates.values()}

    async def update(self, key: str, market_price: float):
        if key in self:
            forex = self[key]
            forex.market_price = market_price

            await self.emit(EventType.TICKER, forex.json())
        else:
            LOG.warning("Attempt to update portfolio with forex rate for %s which is not tracked", key)

    def __contains__(self, key) -> bool:
        return key in self.rates or key in self.rates_by_ticker

    def __getitem__(self, key) -> Forex:
        return self.rates[key] if key in self.rates else self.rates_by_ticker[key]


class Position:
    def __init__(
        self,
        name: str,
        ticker: str,
        volume: float,
        price: float,
        cost: float,
        currency: str,
        asset: c.Asset,
        exchange_rates: ExchangeRates,
    ):
        self.name = name
        self.ticker = ticker
        self.volume = volume
        self.market_price = price
        self.cost = cost
        self.currency = currency
        self.asset = asset
        self.exchange_rates = exchange_rates

    @property
    def market_value(self):
        er = 1.0 if self.currency == "NOK" else self.exchange_rates[self.currency].market_price

        return round(self.volume * self.market_price * er, c.PRECISION)

    @property
    def net_return(self) -> float:
        return round(self.market_value - self.cost, c.PRECISION)

    @property
    def net_return_percent(self) -> float:
        return round(100 * (self.market_value - self.cost) / self.cost, c.PRECISION)

    def json(self):
        return {
            "name": self.name,
            "ticker": self.ticker,
            "volume": self.volume,
            "cost": self.cost,
            "market_price": self.market_price,
            "market_value": self.market_value,
            "net_return": self.net_return,
            "net_return_percent": self.net_return_percent,
            "asset": self.asset.value,
            "currency": self.currency,
        }


class Portfolio(Task):
    def __init__(self, positions):
        super().__init__("Portfolio")
        self.exchange_rates = ExchangeRates()
        self.positions = {p["ticker"]: Position(**p, exchange_rates=self.exchange_rates) for p in positions}
        self.indices = {}
        self.nav_history = []
        self.active_forex = {p.currency for p in self.positions.values()}
        self.running = False
        self._queue = deque([])

    @staticmethod
    def from_config(config_file: Union[Path, str]) -> "Portfolio":
        with open(config_file) as f:
            data = load(f)
            for p in data["positions"]:
                p["asset"] = c.Asset[p["asset"]]
            return Portfolio(data["positions"])

    @property
    def cost(self):
        return round(sum(p.cost for p in self.positions.values()))

    @property
    def net_asset_value(self):
        return round(sum(p.market_value for p in self.positions.values()))

    @property
    def net_return(self):
        return round(self.net_asset_value - self.cost)

    @property
    def net_return_percent(self):
        return round(100 * (self.net_asset_value - self.cost) / (self.cost or 1), c.PRECISION)

    async def update(self, pairs: Union[Tuple[str, float], List[Tuple[str, float]]], initial: bool = False):
        if isinstance(pairs, tuple):
            pairs = [pairs]
        if initial:
            await self._process(pairs, initial=True)
        else:
            self._queue.extend(pairs)

    async def update_index(self, ticker: str, name: str, last: float, change: float, change_7d: float):
        self.indices[ticker] = {"ticker": ticker, "name": name, "last": last, "change": change, "change_7d": change_7d}
        await self.emit(EventType.INDEX, self.indices)
        self.stats.messages += 1

    async def _process(self, pairs: List[Tuple[str, float]], initial: bool = False):
        if not pairs:
            return

        emit_portfolio = False

        for ticker, market_price in pairs:
            if ticker in self.exchange_rates:
                forex = self.exchange_rates[ticker]
                if forex.name in self.active_forex:
                    emit_portfolio = True

                await self.exchange_rates.update(ticker, market_price)
                await self.emit(EventType.TICKER, forex.json())
                self.stats.messages += 1
            elif ticker in self.positions:
                pos = self.positions[ticker]
                if pos.market_price == market_price:
                    continue
                pos.market_price = market_price
                await self.emit(EventType.TICKER, pos.json())
                self.stats.messages += 1
                emit_portfolio = True

        LOG.debug("Portfolio updated: %s", pairs)

        # Skip adding initial updates
        if emit_portfolio and not initial:
            self.nav_history.append(self.net_asset_value)
            self.nav_history = self.nav_history[-100:]
            await self.emit(EventType.PORTFOLIO, self.json())
            self.stats.messages += 1

    def json(self):
        current = self.net_asset_value
        positions = [p.json() for p in self.positions.values()]

        # Enrich with portfolio composition
        composition = {}
        for p in positions:
            alloc = p["market_value"] / current * 100.0
            asset = p["asset"]
            p["allocation"] = round(alloc, 1)
            composition[asset] = composition.get(asset, 0.0) + alloc
        for c, val in composition.items():
            composition[c] = round(val, 1)

        return {
            "market_value": current,
            "net_return": self.net_return,
            "net_return_percent": self.net_return_percent,
            "cost": self.cost,
            "positions": positions,
            "exchange_rates": {f.name: f.json() for f in self.exchange_rates.rates.values()},
            "composition": composition,
            "indices": self.indices,
        }

    async def run(self):
        self.running = True

        while self.running:
            tickers = set()
            latest = []

            while self._queue:
                item = self._queue.pop()
                t = item[0]
                if t not in tickers:
                    tickers.add(t)
                    latest.append(item)

            await self._process(latest)
            await sleep(c.PROCESSING_INTERVAL)

    async def stop(self):
        LOG.info("[%s] Stopping...", self.name)
        self.restart = False
        self.running = False
        LOG.info("[%s] Stopped", self.name)

    def __contains__(self, ticker: str):
        return ticker in self.positions


class DailyCloseTask(Task):
    def __init__(self, portfolio: "Portfolio", db: Database) -> None:
        super().__init__(name="DailyClose")
        self.close = None
        self._db = db
        self._portfolio = portfolio
        portfolio.on(EventType.PORTFOLIO, self.handle_update)

    async def run(self):
        self.running = True

        LOG.info("[%s] Reading previous close", self.name)
        self.close = await self._db.get_last_close()

        if self.close:
            LOG.info("[%s] Last close is %s", self.name, self.close)
            if self.close.m_close != date.today() + timedelta(days=1):
                self.close = DailyClose.create(self.close.m_close)

        while self.running:
            if self.close:
                delta = self._get_wait_time()

                if delta.total_seconds() <= 0:
                    LOG.info("[%s] Persisting %s", self.name, self.close)
                    await self._db.write_close(self.close)
                    self.stats.messages += 1
                    self.close = self.close.next()
                    LOG.info("[%s] Prepared next daily close: %s", self.name, self.close)
                    delta = self._get_wait_time()

                LOG.info("[%s] Waiting %s until next daily close: %s", self.name, delta, self.close)
                await sleep(delta.total_seconds())
            else:
                LOG.debug("[%s] No close object, waiting for portfolio update", self.name)
                await sleep(60)

    async def handle_update(self, event: Event):
        d = event.data["market_value"]
        if self.close:
            self.close.update(d)
        else:
            self.close = DailyClose.create(d)
            LOG.info("[%s] Creating first close object: %s", self.name, self.close)

    async def stop(self):
        LOG.info("[%s] Stopping...", self.name)
        self.restart = False
        self.running = False
        LOG.info("[%s] Stopped", self.name)

    def _get_wait_time(self) -> timedelta:
        now = datetime.now()
        target = datetime.combine(self.close.m_date, time(18))
        delta = target - now

        return delta
