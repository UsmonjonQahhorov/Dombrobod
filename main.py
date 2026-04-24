from db import db
from db.migrations import run_migrations
from bot.handlers import *
import asyncio
from utils.dispatcher import main
from utils.logging_config import setup_logging


async def create_all():
    await db.create_all()


async def run() -> None:
    await create_all()
    await run_migrations()
    await main()


if __name__ == "__main__":
    setup_logging()
    asyncio.run(run())


