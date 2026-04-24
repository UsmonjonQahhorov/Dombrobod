import asyncio
import logging
from typing import Any, Awaitable, Callable, TypeVar

from aiogram.exceptions import TelegramNetworkError

logger = logging.getLogger(__name__)
T = TypeVar("T")


async def with_telegram_retry(
    operation: Callable[[], Awaitable[T]],
    *,
    retries: int = 3,
    base_delay: float = 1.0,
) -> T:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            return await operation()
        except TelegramNetworkError as exc:
            last_error = exc
            if attempt == retries:
                break
            delay = base_delay * attempt
            logger.warning(
                "Telegram network timeout, retrying (%s/%s) in %.1fs: %s",
                attempt,
                retries,
                delay,
                exc,
            )
            await asyncio.sleep(delay)
    raise last_error if last_error else RuntimeError("Unknown Telegram retry error")


async def safe_answer(message, text: str, **kwargs: Any) -> bool:
    try:
        await with_telegram_retry(lambda: message.answer(text, **kwargs))
        return True
    except TelegramNetworkError as exc:
        logger.error("Failed to send message.answer after retries: %s", exc)
        return False
