import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware

from utils.db_scope import release_db_session

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
            logger.debug("Cleaning scoped DB session after update")
            await release_db_session()
