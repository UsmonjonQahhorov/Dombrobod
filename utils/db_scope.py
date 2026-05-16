import inspect
import logging
from contextlib import asynccontextmanager

from db import db

logger = logging.getLogger(__name__)


async def release_db_session() -> None:
    """Return the current task's scoped SQLAlchemy session to the pool."""
    maybe_awaitable = db.remove()
    if inspect.isawaitable(maybe_awaitable):
        await maybe_awaitable


@asynccontextmanager
async def db_session_scope():
    """
    Scoped DB session for background tasks and scheduler jobs.
    Handlers should rely on DbSessionCleanupMiddleware instead.
    """
    try:
        yield
    finally:
        logger.debug("Cleaning scoped DB session")
        await release_db_session()
