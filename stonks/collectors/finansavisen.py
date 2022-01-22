"""Finansavisen collector"""

import asyncio
from logging import getLogger
from uuid import uuid4

from ..portfolio import Portfolio
from .base import WSClientTask

LOG = getLogger(__name__)


class Finansavisen(WSClientTask):
    def __init__(self, portfolio: Portfolio):
        super().__init__(
            "wss://bors.finansavisen.no/server/components", "https://bors.finansavisen.no", name="Finansavisen"
        )
        self.portfolio = portfolio
        self.subtasks = []

    async def run(self):
        await self.connect()
        self.subtasks = [asyncio.create_task(self._ping_task())]
        await self.subscribe()

        try:
            await self.receive()
        except Exception as e:
            LOG.error("[%s] Exception during recv: %s (%s)", self.name, self.ws, e)
            self.stats.errors += 1

        LOG.warning("[%s] Disconnected", self.name)
        await self.session.close()

    async def subscribe(self):
        chan = str(uuid4())
        cols = "ITEM%2CLONG_NAME%2CLAST"
        req = "subscribe?initiatorComponent=Quotelist&source=feed.ob.quotes.EQUITIES%2BPCC"
        req += f"&columns={cols}&channel={chan}"

        LOG.info("[%s] Subscribing to all tickers with channel id %s", self.name, chan)
        await self.ws.send_str(req)

        chan = str(uuid4())
        cols = "CHANGE_7DAYS_PCT%2CCHANGE_PCT%2CLAST"
        req = f"subscribe?itemSector=OSEBX.OSE&columns={cols}&channel={chan}"

        LOG.info("[%s] Subscribing to OSEBX Index with channel id %s", self.name, chan)
        await self.ws.send_str(req)

    async def receive(self):
        async for msg in self.ws:
            self.stats.messages += 1
            if msg.data == "pong":
                continue

            data = msg.json()

            if "values" not in data:
                continue

            msg_type = data["type"]
            values = data["values"]

            if msg_type == "meta" and "initial_data_sent" in values and values["initial_data_sent"]:
                LOG.info("[%s] Initial data received", self.name)
                continue

            ticker = data["key"]
            initial = msg_type == "new"

            if ticker == "OSEBX_OSE":
                await self.portfolio.update_index(
                    ticker,
                    "Oslo Børs (OSEBX)",
                    values.get("LAST", 0) or 0.0,
                    round(values.get("CHANGE_PCT") or 0.0, 2),
                    round(values.get("CHANGE_7DAYS_PCT") or 0.0, 2),
                )

            if ticker in self.portfolio:
                if "LAST" in values and values["LAST"] is not None:
                    await self.portfolio.update((ticker, values["LAST"]), initial=initial)

    async def stop(self):
        await super().stop()
        LOG.debug("[%s] Stopping subtasks ...", self.name)
        for t in self.subtasks:
            t.cancel()
            await t
        LOG.debug("[%s] Subtasks stopped", self.name)

    async def _ping_task(self):
        while True:
            await asyncio.sleep(30)
            await self.ws.send_str("ping")