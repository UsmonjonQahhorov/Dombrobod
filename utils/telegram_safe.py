import asyncio
import logging
import random
from typing import Any, Awaitable, Callable, TypeVar

from aiogram.exceptions import TelegramNetworkError

logger = logging.getLogger(__name__)
T = TypeVar("T")


async def with_telegram_retry(
    operation: Callable[[], Awaitable[T]],
    *,
    retries: int = 2,
    base_delay: float = 0.15,
    max_delay: float = 0.6,
    operation_timeout: float = 6.0,
) -> T:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            return await asyncio.wait_for(operation(), timeout=operation_timeout)
        except TelegramNetworkError as exc:
            last_error = exc
        except asyncio.TimeoutError as exc:
            last_error = exc

        if attempt == retries:
            break

        delay = min(max_delay, base_delay * (2 ** (attempt - 1))) + random.uniform(0.0, 0.4)
        logger.warning(
            "Telegram timeout, retrying (%s/%s) in %.2fs: %s",
            attempt,
            retries,
            delay,
            last_error,
        )
        await asyncio.sleep(delay)
    raise last_error if last_error else RuntimeError("Unknown Telegram retry error")


async def safe_answer(message, text: str, **kwargs: Any) -> bool:
    kwargs.setdefault("request_timeout", 6)
    try:
        await with_telegram_retry(
            lambda: message.answer(text, **kwargs),
            retries=2,
            base_delay=0.15,
            max_delay=0.6,
            operation_timeout=6.0,
        )
        return True
    except Exception as exc:
        logger.error("Failed to send message.answer after retries: %s", exc)
        return False
