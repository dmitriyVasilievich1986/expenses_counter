"""Error handler for DAO methods."""

__all__ = ("error_handler",)

from typing import Any, Callable, TypeVar

from loguru import logger
from sqlalchemy.exc import DatabaseError, IntegrityError, NoResultFound

from .exceptions import DBException, NotFoundException, RelationshipNotFoundException

R = TypeVar("R")


def error_handler(func: Callable[..., R]) -> R:
    """Decorator for handling database errors in async DAO methods.

    This decorator wraps async methods to catch common database exceptions
    and convert them into application-specific exceptions with appropriate logging.

    Args:
        func: The async function to be wrapped.

    Returns:
        The wrapped function with error handling.

    Raises:
        NotFoundException: When a database record is not found.
        RelationshipNotFoundException: When a foreign key constraint is violated.
        DBException: For general database errors.

    """

    async def wrapper(self: Any, *args: Any, **kwargs: Any) -> R:
        try:
            return await func(self, *args, **kwargs)
        except NoResultFound as e:
            logger.error(f"Error in {func.__name__}: {e}")
            raise NotFoundException() from e
        except IntegrityError as e:
            logger.error(f"Error in {func.__name__}: {e}")
            raise RelationshipNotFoundException() from e
        except DatabaseError as e:
            logger.error(f"Error in {func.__name__}: {e}")
            raise DBException() from e

    return wrapper
