from functools import wraps

from pydantic import ValidationError


def safe_tool(func):
    """
    Decorator: Convert all internal exceptions into structured MCP-safe error messages,
    instead of letting them raise.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except ValidationError as ve:
            return [f"Validation error: {ve.errors()}"]

        except Exception as e:
            return [f"Tool execution error: {str(e)}"]

    return wrapper
