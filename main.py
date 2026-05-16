import asyncio
import logging

from bot.handlers import *
from db import db
from db.migrations import run_migrations
from utils.dispatcher import main
from utils.logging_config import setup_logging

logger = logging.getLogger(__name__)


def _asyncio_exception_handler(loop: asyncio.AbstractEventLoop, context: dict) -> None:
    """Log background task failures instead of failing silently."""
    exc = context.get("exception")
    if exc is not None:
        logger.error("Unhandled asyncio exception: %s", context.get("message"), exc_info=exc)
    else:
        logger.error("Asyncio error: %s", context)


async def create_all():
    await db.create_all()


async def run() -> None:
    await create_all()
    await run_migrations()
    await main()


if __name__ == "__main__":
    setup_logging()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.set_exception_handler(_asyncio_exception_handler)
    try:
        loop.run_until_complete(run())
    finally:
        loop.close()


