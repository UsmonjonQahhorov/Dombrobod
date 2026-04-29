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

# Controlled outgoing Telegram queue for scheduler/cron-driven bursts.
#
# The queue is intentionally processed by a single worker with a small throttle
# to prevent APScheduler from creating a "mini DDoS" against Telegram.
TELEGRAM_SEND_QUEUE_MAXSIZE = 5000
_telegram_send_queue: asyncio.Queue[
    tuple[Callable[[], Awaitable[Any]], asyncio.Future[Any]]
] = asyncio.Queue(maxsize=TELEGRAM_SEND_QUEUE_MAXSIZE)
_telegram_worker_task: asyncio.Task[None] | None = None
_telegram_worker_started = False


async def telegram_enqueue(operation: Callable[[], Awaitable[T]]) -> T:
    """
    Enqueue a Telegram operation to be executed by the single worker.
    The caller awaits the result to allow scheduler cleanup logic to run.
    """
    loop = asyncio.get_running_loop()
    fut: asyncio.Future[T] = loop.create_future()
    # Store Future[Any] internally; types are safe due to runtime set_result.
    await _telegram_send_queue.put((operation, fut))  # type: ignore[arg-type]
    return await fut


async def telegram_worker(bot: Any, *, throttle_seconds: float = 0.3) -> None:
    while True:
        operation, fut_any = await _telegram_send_queue.get()
        try:
            result = await with_telegram_retry(operation, retries=1, operation_timeout=2.5)
            fut_any.set_result(result)
        except Exception as exc:
            fut_any.set_exception(exc)
        finally:
            _telegram_send_queue.task_done()
        if throttle_seconds > 0:
            await asyncio.sleep(throttle_seconds)


def start_telegram_worker(bot: Any) -> None:
    global _telegram_worker_task, _telegram_worker_started
    if _telegram_worker_started and _telegram_worker_task and not _telegram_worker_task.done():
        return
    _telegram_worker_started = True
    _telegram_worker_task = asyncio.create_task(telegram_worker(bot))


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
