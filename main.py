from db import db
from bot.handlers import *
import logging
import sys
import asyncio
from utils.dispatcher import main


async def create_all():
    await db.create_all()


async def run() -> None:
    await create_all()
    await main()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logging.getLogger('aiogram.event').setLevel(logging.WARNING)
    asyncio.run(run())


