"""Data collector base classes"""

from abc import abstractmethod
import asyncio
from logging import getLogger
from typing import Dict, Optional

import aiohttp

from ..portfolio import Portfolio
from ..task import Task

LOG = getLogger(__name__)


class WSClientTask(Task):
    def __init__(
        self,
        uri: str,
        origin: str,
        cookie: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.session = None
        self.ws = None
        self._uri = uri
        self._origin = origin
        self._headers = headers or {}
        if cookie:
            self._headers["Cookie"] = cookie

    async def connect(self, **kwargs):
        self.session = aiohttp.ClientSession()
        self.ws = await self.session.ws_connect(self._uri, origin=self._origin, headers=self._headers, **kwargs)

        LOG.info("[%s] Connected to server", self.name)

    async def stop(self):
        LOG.info("[%s] Stopping...", self.name)

        self.restart = False
        if self.ws:
            LOG.debug("[%s] Closing WebSocket", self.name)
            await self.ws.close()
            self.ws = None
        if self.session:
            LOG.debug("[%s] Closing ClientSession", self.name)
            await self.session.close()
            self.session = None

        LOG.info("[%s] Stopped", self.name)


class HTTPClientTask(Task):
    def __init__(self, portfolio: Portfolio, *args, interval: int = 60, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.portfolio = portfolio
        self.interval = interval
        self.session = None
        self.running = False
        self.initial = True

    @abstractmethod
    async def collect(self):
        raise NotImplementedError()

    async def run(self):
        self.running = True

        while self.running:
            self.session = aiohttp.ClientSession()
            async with self.session:
                try:
                    await self.collect()
                except Exception as e:
                    LOG.error("[%s] Failed to collect: %s", self.name, e)
                    self.stats.errors += 1

            self.initial = False
            await asyncio.sleep(self.interval)

    async def stop(self):
        LOG.info("[%s] Stopping...", self.name)

        self.restart = False
        if self.session is not None:
            await self.session.close()
        self.running = False

        LOG.info("[%s] Stopped", self.name)
