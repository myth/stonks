"""Custom serializer"""

from datetime import date, datetime
from functools import partial
from json import JSONEncoder, dumps

from .db import DailyClose
from .events import Event, EventType
from .portfolio import Portfolio


class StonksEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (DailyClose, Event, Portfolio)):
            return obj.json()
        elif isinstance(obj, EventType):
            return obj.value
        elif isinstance(obj, (date, datetime)):
            return obj.isoformat()
        # Let the base class default method raise the TypeError
        return super().default(obj)


serialize = partial(dumps, cls=StonksEncoder)
