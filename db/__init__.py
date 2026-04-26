import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, AsyncAttrs, async_scoped_session, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from db.config import Config


class Base(AsyncAttrs, DeclarativeBase):
    pass


class AsyncDatabaseSession:
    def __init__(self):
        self._session = None
        self._engine = None

    def __getattr__(self, name):
        return getattr(self._session, name)

    def init(self):
        self._engine = create_async_engine(
            Config.DB_CONFIG,
            future=True,
            echo=False,
            pool_pre_ping=True,
        )
        session_factory = sessionmaker(self._engine, expire_on_commit=False, class_=AsyncSession)
        self._session = async_scoped_session(session_factory, scopefunc=asyncio.current_task)

    async def create_all(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


db = AsyncDatabaseSession()
