import logging
import os

from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from bot.handlers.start_handler import main_router
from db import db

load_dotenv()
TOKEN = os.getenv("TOKEN")
dp = Dispatcher()
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


async def main() -> None:
    await dp.start_polling(bot)
    logging.basicConfig(level=logging.WARNING)
