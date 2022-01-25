"""Async, event emitting, self-restarting task"""

from abc import ABC, abstractmethod
from asyncio import sleep
from datetime import datetime, timedelta
from logging import getLogger
from typing import Optional

from .config import TASK_RESTART_MIN_WAIT_TIME
from .events import EventEmitter

LOG = getLogger(__name__)


class TaskStats:
    def __init__(self):
        self.messages = 0
        self.errors = 0
        self.restarts = 0

    def json(self):
        return {
            "messages": self.messages,
            "errors": self.errors,
            "restarts": self.restarts,
        }


class Task(ABC, EventEmitter):
    def __init__(self, name: str, **kwargs):
        super().__init__(**kwargs)
        self.name: str = name
        self.stats = TaskStats()
        self._started: Optional[datetime] = None
        self._stopped: Optional[datetime] = None
        self.restart = True

    async def start(self):
        LOG.info("[%s] Starting task...", self.name)

        while self.restart:
            self._stopped = None
            self._started = datetime.now()
            try:
                await self.run()
            except Exception as e:
                LOG.exception(e)
                self.stats.errors += 1
            self._stopped = datetime.now()
            elapsed = self._stopped - self._started

            if self.restart:
                log = "[%s] Completed after %s, restarting task %s"
                self.stats.restarts += 1
                if elapsed < timedelta(seconds=TASK_RESTART_MIN_WAIT_TIME):
                    LOG.info(log, self.name, elapsed, f" in {TASK_RESTART_MIN_WAIT_TIME} seconds")
                    await sleep(TASK_RESTART_MIN_WAIT_TIME)
                else:
                    LOG.info(log, self.name, elapsed, "")

            self._started = None

    @abstractmethod
    async def run(self):
        pass

    @abstractmethod
    async def stop(self):
        pass

    def __repr__(self) -> str:
        return f"Task<'{self.name}'>"
