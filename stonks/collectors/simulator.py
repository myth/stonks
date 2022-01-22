"""Collection simulator"""

from asyncio import sleep
from logging import getLogger
from random import choice, random

from ..config import SIMULATOR_MAX_TICKER_INTERVAL
from ..portfolio import Portfolio
from ..task import Task

LOG = getLogger(__name__)


class Simulator(Task):
    """
    Data collection simulator that will generate random ticker events based on the existing
    entries in the portfolio. Make sure there are some entries in the config file first.
    """

    def __init__(self, portfolio: Portfolio) -> None:
        super().__init__(name="Simulator")
        self.portfolio = portfolio
        self.running = False

    async def run(self):
        self.running = True

        while self.running:
            if self.portfolio.positions:
                t = choice(list(self.portfolio.positions.values()))
                last = t.market_price
                new = last + (random() - 0.5) * last * 0.02
                await self.portfolio.update((t.ticker, round(new, 2)))
            else:
                LOG.error("[%s] Cannot simulate, no positions in portfolio", self.name)
            await sleep(random() * SIMULATOR_MAX_TICKER_INTERVAL)

    async def stop(self):
        LOG.info("[%s] Stopping...", self.name)
        self.restart = False
        self.running = False
        LOG.info("[%s] Stopped", self.name)
