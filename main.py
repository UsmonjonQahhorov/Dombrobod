from db import db
from bot.handlers import *
import logging
import sys
import asyncio
from utils.dispatcher import main, bot
from utils.scheduler import scheduler


async def create_all():
    await db.create_all()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logging.getLogger('aiogram.event').setLevel(logging.WARNING)
    bot.delete_webhook(drop_pending_updates=True)
    asyncio.run(main())
    scheduler.start()


