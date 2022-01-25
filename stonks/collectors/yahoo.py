"""Yahoo Finance Collector"""

from asyncio import sleep
from datetime import datetime, timedelta
from logging import getLogger

from ..config import Asset
from .base import HTTPClientTask

LOG = getLogger(__name__)
URL = "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=1d&interval=1m"


class YahooFinance(HTTPClientTask):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, name="YahooFinance", interval=60, **kwargs)

    async def collect(self):
        LOG.info("[%s] Collecting market prices", self.name)

        for pos in self.portfolio.positions.values():
            if pos.asset not in (Asset.ETF, Asset.INDEX_ETF):
                continue
            ticker = pos.ticker
            LOG.debug("[%s] Collecting market price for %s", self.name, ticker)

            try:
                async with self.session.get(URL.format(ticker=ticker)) as resp:
                    nav = None
                    self.stats.messages += 1
                    data = await resp.json()
                    meta = data["chart"]["result"][0]["meta"]
                    quote = data["chart"]["result"][0]["indicators"]["quote"][0]

                    if quote:
                        for i in reversed(quote.get("close")):
                            if i is not None:
                                nav = round(i, 4)
                                break
                    else:
                        LOG.debug("[%s] No quote available for %s, grabbing previous close", self.name, ticker)
                        nav = round(meta["previousClose"], 4)
                    if nav is not None:
                        await self.portfolio.update((ticker, nav), initial=self.initial)
            except Exception as e:
                LOG.error("[%s] Failed to collect market price for: %s: %s", self.name, ticker, e)
                self.stats.errors += 1
            await sleep(1)

        now = datetime.now()
        if (now.hour > 18 or now.hour < 8):
            if self.interval != 3600:
                LOG.info("[%s] Switching to hourly interval, now outside market hours", self.name)
                self.interval = 3600
        elif self.interval != 60:
            LOG.info("[%s] Switching to one minute interval, now approaching market hours", self.name)
            self.interval = 60

        LOG.info("[%s] Market prices collected, sleeping for %s", self.name, timedelta(seconds=self.interval))
