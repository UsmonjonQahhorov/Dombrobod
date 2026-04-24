import logging
import os

from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from utils.scheduler import ensure_scheduler_started, restore_jobs_from_db

load_dotenv()
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise RuntimeError("TOKEN is missing. Set it in environment or .env file.")

dp = Dispatcher()
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


async def main() -> None:
    ensure_scheduler_started()
    logging.getLogger(__name__).info("Starting bot polling")
    # Ensure polling works even if webhook was previously configured.
    await bot.delete_webhook(drop_pending_updates=False)
    await restore_jobs_from_db()
    await dp.start_polling(bot)
