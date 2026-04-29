import asyncio
import logging
from typing import Any, Awaitable, Callable, TypeVar

from aiogram.exceptions import TelegramNetworkError

logger = logging.getLogger(__name__)
T = TypeVar("T")

#
# Global limiter to keep Telegram API calls bounded under burst load.
# This prevents scheduler/user bursts from creating "concurrency explosions".
#
TELEGRAM_SEND_SEMAPHORE = asyncio.Semaphore(4)


async def with_telegram_retry(
    operation: Callable[[], Awaitable[T]],
    *,
    retries: int = 1,
    operation_timeout: float = 2.5,
) -> T:
    last_error: Exception | None = None
    # `retries` here means "total attempts" (i.e. 1 == fail fast, 2 == retry once).
    for attempt in range(1, retries + 1):
        try:
            # Acquire semaphore per-attempt to avoid holding capacity while sleeping.
            async with TELEGRAM_SEND_SEMAPHORE:
                return await asyncio.wait_for(operation(), timeout=operation_timeout)
        except (TelegramNetworkError, asyncio.TimeoutError) as exc:
            last_error = exc
            if attempt == retries:
                break
    raise last_error if last_error else RuntimeError("Unknown Telegram retry error")


async def safe_answer(message, text: str, **kwargs: Any) -> bool:
    # Keep user-facing operations bounded to avoid multi-minute hangs.
    kwargs.setdefault("request_timeout", 2.5)
    try:
        await with_telegram_retry(lambda: message.answer(text, **kwargs), retries=1, operation_timeout=2.5)
        return True
    except Exception as exc:
        logger.error("Failed to send message.answer after retries: %s", exc)
        return False
