import logging
import os

from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramNetworkError
from dotenv import load_dotenv
from utils.db_session_middleware import DbSessionCleanupMiddleware
from utils.scheduler import ensure_scheduler_started, restore_jobs_from_db
from utils.telegram_safe import start_telegram_worker, with_telegram_retry

load_dotenv()
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise RuntimeError("TOKEN is missing. Set it in environment or .env file.")

dp = Dispatcher()
dp.update.outer_middleware(DbSessionCleanupMiddleware())

bot = Bot(
    TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)


async def main() -> None:
    ensure_scheduler_started()
    logging.getLogger(__name__).info("Starting bot polling")
    # Ensure polling works even if webhook was previously configured.
    try:
        await with_telegram_retry(
            lambda: bot.delete_webhook(drop_pending_updates=True),
            retries=1,
            operation_timeout=2.5,
        )
    except TelegramNetworkError as exc:
        logging.getLogger(__name__).warning("delete_webhook failed after retries: %s", exc)
    await restore_jobs_from_db()
    # Start a single Telegram worker for scheduler-driven bursts.
    start_telegram_worker(bot)
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()
