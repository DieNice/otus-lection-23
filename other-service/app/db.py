from pydantic import PostgresDsn
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import config


def get_async_engine(conn: PostgresDsn) -> AsyncEngine:
    return create_async_engine(
        conn.unicode_string(),
    )


def get_async_session(engine: AsyncEngine) -> AsyncSession:
    return async_sessionmaker(engine, expire_on_commit=False)


_engine = get_async_engine(config.database_uri)
async_session = get_async_session(_engine)
