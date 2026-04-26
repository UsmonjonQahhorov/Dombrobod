import inspect
import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware

from db import db

logger = logging.getLogger(__name__)


class DbSessionCleanupMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        finally:
            # Always clear task-local scoped session state after each update.
            logger.debug("Cleaning scoped DB session after update")
            maybe_awaitable = db.remove()
            if inspect.isawaitable(maybe_awaitable):
                await maybe_awaitable
