"""Stonks Dashboard App"""

from argparse import Namespace
import asyncio
from logging import getLogger
from os.path import join
from weakref import WeakSet

from aiohttp import WSMsgType, web

from . import __version__
from . import config as c
from .collectors.euronext import EuronextForex
from .collectors.finansavisen import Finansavisen
from .collectors.nordnet import NordNetFunds
from .collectors.simulator import Simulator
from .collectors.yahoo import YahooFinance
from .db import Database
from .events import Event, EventType
from .portfolio import Portfolio
from .serialize import serialize

LOG = getLogger(__name__)


class Stonks:
    def __init__(self, args: Namespace):
        self.app = web.Application()
        self.db = Database(f"sqlite+aiosqlite:///{args.db}" if args.db else "sqlite+aiosqlite://")
        self.portfolio = Portfolio.from_config(args.config, self.db) if args.config else Portfolio(self.db, [])
        self.collectors = [
            self.portfolio,
            NordNetFunds(self.portfolio),
            EuronextForex(self.portfolio),
            YahooFinance(self.portfolio),
            Finansavisen(self.portfolio),
        ]
        self._tasks = []

        self.app["clients"] = WeakSet()
        self.app.add_routes([web.get("/", self.get_index), web.get("/ws", self.get_ws)])
        self.app.router.add_static("/static/", path=join(c.PUB_ROOT, "static"), name="static")
        self.app.on_startup.append(self.on_startup)
        self.app.on_shutdown.append(self.on_shutdown)

        # Subscribe to portfolio events that should be broadcast to the dashboard
        for et in (EventType.TICKER, EventType.PORTFOLIO, EventType.INDEX, EventType.CHART, EventType.CHART_TICK):
            self.portfolio.on(et, self.broadcast)

        if args.simulate:
            LOG.warning("Simulator active!")
            self.collectors.append(Simulator(self.portfolio))

    def run(self):
        LOG.info("Starting Stonks %s", __version__)
        web.run_app(self.app)

    async def get_index(self, request):
        return web.FileResponse(join(c.PUB_ROOT, "index.html"))

    async def get_ws(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        clients = self.app["clients"]
        clients.add(ws)

        LOG.info("[WS] Client connected %s (connected: %d)", request.remote, len(clients))
        await ws.send_json(Event(EventType.PORTFOLIO, self.portfolio).json(), dumps=serialize)
        await ws.send_json(Event(EventType.CHART, self.portfolio.history.json()).json(), dumps=serialize)

        async for msg in ws:
            LOG.debug("[WS] Received msg: %s", msg)

            if msg.type == WSMsgType.TEXT:
                if msg.data == "close":
                    await ws.close()
                    LOG.info("[WS] Closed %s", ws)
            elif msg.type == WSMsgType.ERROR:
                LOG.error("[WS] Closed with unexpected error")
                LOG.exception(ws.exception())
            elif msg.type in (WSMsgType.CLOSING, WSMsgType.CLOSED):
                await ws.close()
                LOG.info("[WS] Closed %s", ws)

        clients.remove(ws)
        LOG.info("[WS] Closed %s (connected: %d)", request.remote, len(clients))

        return ws

    async def broadcast(self, e: Event):
        for client in self.app["clients"]:
            try:
                await client.send_json(e.json(), dumps=serialize)
            except Exception as e:
                LOG.error("[WS] Failed to broadcast to client: %s", e)

    async def on_startup(self, app):
        await self.db.initialize()
        LOG.debug("Spawning tasks for %d collectors", len(self.collectors))
        self._tasks.extend(asyncio.create_task(c.start(), name=c.name) for c in self.collectors)
        self._tasks.append(asyncio.create_task(self.push_status(), name="status"))

    async def on_shutdown(self, app):
        LOG.info("Stopping Stonks")

        for c in self.collectors:
            await c.stop()
        await self.db.stop()
        for t in self._tasks:
            LOG.debug("Cancelling task %s ...", t.get_name())
            try:
                t.cancel()
                await t
            except Exception:
                LOG.exception(t.exception())

        LOG.info("Stonks stopped")

    async def push_status(self):
        while True:
            await asyncio.sleep(1)
            e = Event(EventType.STATUS, {c.name: c.stats.json() for c in self.collectors})
            await self.broadcast(e)
