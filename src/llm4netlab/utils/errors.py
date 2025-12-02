import asyncio
from functools import wraps
from typing import Any, Callable

from pydantic import ValidationError


def safe_tool(func: Callable) -> Callable:
    """
    Decorator: Convert all internal exceptions into structured MCP-safe error messages,
    instead of letting them raise.
    """

    if asyncio.iscoroutinefunction(func):

        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except ValidationError as ve:
                return {"error": "validation_error", "details": ve.errors()}
            except Exception as e:
                return {"error": "tool_execution_error", "details": str(e)}

        return async_wrapper

    else:

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except ValidationError as ve:
                return {"error": "validation_error", "details": ve.errors()}
            except Exception as e:
                return {"error": "tool_execution_error", "details": str(e)}

        return sync_wrapper
