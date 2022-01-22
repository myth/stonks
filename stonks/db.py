"""Historical database"""

from datetime import date
from logging import getLogger
from typing import NamedTuple, Optional

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


class Close(NamedTuple):
    date: date
    open: int
    close: int
    high: int
    low: int


class Database:
    def __init__(self, connection_string: str = "sqlite+aiosqlite://") -> None:
        self.engine: AsyncEngine = create_async_engine(connection_string)
        LOG.info("[DB] Created database: %s", self.engine)

    async def initialize(self):
        LOG.info("[DB] Initializing database table")
        async with self.engine.begin() as conn:
            await conn.run_sync(metadata.create_all)
        LOG.info("[DB] Database table initialized")

    async def get_last_close(self) -> Optional[Close]:
        async with self.engine.begin() as conn:
            stmt = close_table.select().order_by(-close_table.c.date).limit(1)
            result = await conn.execute(stmt)
            if result:
                return Close(*result.fetchone())

    async def write_close(self, close: Close):
        async with self.engine.begin() as conn:
            stmt = close_table.insert().values(**close._asdict())
            await conn.execute(stmt)

    async def stop(self):
        LOG.info("[DB] Disposing database engine")
        await self.engine.dispose()
        LOG.info("[DB] Database engine disposed")

    def __repr__(self) -> str:
        return self.engine
