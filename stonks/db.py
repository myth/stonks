"""Historical database"""

from datetime import date, datetime, timedelta
from logging import getLogger
from typing import Any, Dict, Optional

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

LOG = getLogger(__name__)

metadata = sa.MetaData()
close_table = sa.Table(
    "close",
    metadata,
    sa.Column("date", sa.Date, primary_key=True),
    sa.Column("open", sa.Integer, nullable=False),
    sa.Column("close", sa.Integer, nullable=False),
    sa.Column("high", sa.Integer, nullable=False),
    sa.Column("low", sa.Integer, nullable=False),
)


class DailyClose:
    def __init__(self, m_date: date, m_open: int, m_close: int, m_high: int, m_low: int) -> None:
        self.m_date = m_date
        self.m_open = m_open
        self.m_close = m_close
        self.m_high = m_high
        self.m_low = m_low

    def update(self, market_value: int):
        self.m_close = market_value
        if market_value > self.m_high:
            self.m_high = market_value
        elif market_value < self.m_low:
            self.m_low = market_value

    def next(self) -> "DailyClose":
        return DailyClose(self.m_date + timedelta(days=1), self.m_close, self.m_close, self.m_close, self.m_close)

    def json(self) -> Dict[str, Any]:
        return {f.replace("m_", ""): v for f, v in self.__dict__.items() if f.startswith("m_")}

    @classmethod
    def create(cls, market_value: int) -> "DailyClose":
        now = datetime.now()
        day = now.date() if now.hour < 18 else now.date() + timedelta(days=1)

        return DailyClose(day, market_value, market_value, market_value, market_value)

    def __repr__(self) -> str:
        return "DailyClose<{date}>(open={open} close={close} high={high} low={low})".format(
            date=self.m_date,
            open=self.m_open,
            close=self.m_close,
            high=self.m_high,
            low=self.m_low
        )


class Database:
    def __init__(self, connection_string: str = "sqlite+aiosqlite://") -> None:
        self.engine: AsyncEngine = create_async_engine(connection_string)
        LOG.info("[DB] Created database: %s", self.engine)

    async def initialize(self):
        LOG.info("[DB] Initializing database table")
        async with self.engine.begin() as conn:
            await conn.run_sync(metadata.create_all)
        LOG.info("[DB] Database table initialized")

    async def get_last_close(self) -> Optional[DailyClose]:
        async with self.engine.begin() as conn:
            stmt = close_table.select().order_by(-close_table.c.date).limit(1)
            result = await conn.execute(stmt)
            result = result.fetchone()
            if result:
                return DailyClose(*result)

    async def write_close(self, close: DailyClose):
        async with self.engine.begin() as conn:
            stmt = close_table.insert().values(**close.json())
            await conn.execute(stmt)

    async def stop(self):
        LOG.info("[DB] Disposing database engine")
        await self.engine.dispose()
        LOG.info("[DB] Database engine disposed")

    def __repr__(self) -> str:
        return self.engine
