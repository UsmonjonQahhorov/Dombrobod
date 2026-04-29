import logging
import os
import asyncio

from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramNetworkError
from aiogram.utils.backoff import BackoffConfig
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


async def telegram_watchdog(*, fail_limit: int = 20, interval_seconds: float = 15.0) -> None:
    fails = 0
    while True:
        try:
            await with_telegram_retry(lambda: bot.get_me(), retries=1, operation_timeout=10.0)
            if fails:
                logging.getLogger(__name__).warning("Telegram watchdog recovered after %s failures", fails)
            fails = 0
        except Exception as exc:
            fails += 1
            logging.getLogger(__name__).warning(
                "Telegram watchdog failure %s/%s: %r (%s)",
                fails,
                fail_limit,
                exc,
                type(exc).__name__,
            )
            if fails >= fail_limit:
                logging.getLogger(__name__).error("Telegram unreachable too long, exiting for docker restart")
                os._exit(1)
        await asyncio.sleep(interval_seconds)


async def main() -> None:
    ensure_scheduler_started()
    logging.getLogger(__name__).info("Starting bot polling")
    # Ensure polling works even if webhook was previously configured.
    try:
        await with_telegram_retry(
            lambda: bot.delete_webhook(drop_pending_updates=True),
            retries=2,
            operation_timeout=10.0,
        )
    except TelegramNetworkError as exc:
        logging.getLogger(__name__).warning("delete_webhook failed after retries: %s", exc)
    await restore_jobs_from_db()
    # Start a single Telegram worker for scheduler-driven bursts.
    start_telegram_worker(bot)
    asyncio.create_task(telegram_watchdog())
    backoff_config = BackoffConfig(min_delay=0.5, max_delay=2.0, factor=1.3, jitter=0.1)
    try:
        await dp.start_polling(
            bot,
            skip_updates=True,
            polling_timeout=20,
            backoff_config=backoff_config,
        )
    finally:
        await bot.session.close()
