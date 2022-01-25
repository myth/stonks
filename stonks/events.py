"""Events"""

from enum import Enum
from typing import Any, Dict, Coroutine, NamedTuple, Optional


class EventType(Enum):
    STATUS: str = "status"
    PORTFOLIO: str = "portfolio"
    TICKER: str = "ticker"
    CHART: str = "chart"
    INDEX: str = "index"
    CLOSE: str = "close"


class Event(NamedTuple):
    type: EventType
    data: Optional[Any] = None

    def json(self) -> Dict[str, Any]:
        return {"type": self.type.value, "data": self.data}

    def __repr__(self) -> str:
        return f"Event<{self.type.name}>(data={self.data})"


class EventEmitter:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._observers = {}

    async def emit(self, e: EventType, payload: Optional[Any] = None):
        if e in self._observers:
            event = Event(e, payload)
            for cb in self._observers[e]:
                await cb(event)

    def on(self, e: EventType, cb: Coroutine):
        self._observers.setdefault(e, set()).add(cb)

    def off(self, e: EventType, cb: Coroutine):
        if e in self._observers:
            self._observers[e].remove(cb)
