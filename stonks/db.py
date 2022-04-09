"""Historical database"""

from logging import getLogger
from typing import List

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from .config import HISTORY_BUFFER
from .history import CandleStick

LOG = getLogger(__name__)

metadata = sa.MetaData()
history_table = sa.Table(
    "history",
    metadata,
    sa.Column("time", sa.Integer, primary_key=True),
    sa.Column("open", sa.Integer, nullable=False),
    sa.Column("high", sa.Integer, nullable=False),
    sa.Column("low", sa.Integer, nullable=False),
    sa.Column("close", sa.Integer, nullable=False),
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

    async def write_candlestick(self, c: CandleStick):
        async with self.engine.begin() as conn:
            stmt = history_table.insert().values(**c.json())
            await conn.execute(stmt)
            LOG.info("[DB] Wrote %s to history", c)

    async def get_history(self, count: int = HISTORY_BUFFER) -> List[CandleStick]:
        async with self.engine.begin() as conn:
            stmt = history_table.select().order_by(-history_table.c.time).limit(count)
            result = await conn.execute(stmt)
            return sorted([CandleStick.create_from_db(*c) for c in result.fetchall()], key=lambda c: c.time)

    async def stop(self):
        LOG.info("[DB] Disposing database engine")
        await self.engine.dispose()
        LOG.info("[DB] Database engine disposed")

    def __repr__(self) -> str:
        return self.engine
