from typing import Any, Callable


def get_context_string(
    func: Callable[..., Any]
) -> str:
    """Extract a human-readable function execution context string.

    Args:
        func: The function or callable object being decorated.

    Returns:
        A formatted string describing the function's module and qualified name
        for diagnostic exception messaging.
    """

    # 1. Safely extract function qualification name and module metadata with defensive fallbacks
    func_name = getattr(func, "__qualname__", getattr(func, "__name__", "callable"))
    func_module = getattr(func, "__module__", None)

    # 2. Format and return context string including module prefix if available
    if func_module:
        return f"Function {func_module}.{func_name}()"
    return f"Function {func_name}()"


_DESIGN_NOTES = """
# get_context_string — validate_call Context Builder

## Purpose
Safely extracts human-readable diagnostic metadata (`__module__` and `__qualname__`)
from target callables at decoration time. Isolates defensive reflection logic 
and IDE inspection handling away from the main `@validate_call` decorator body.
"""