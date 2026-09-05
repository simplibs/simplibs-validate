from typing import Any, Callable, TypedDict


class FuncContextInfo(TypedDict):
    name: str
    module: str | None


def get_context_info(func: Callable[..., Any]) -> FuncContextInfo:
    """Extract safe execution metadata from a decorated callable.

    Args:
        func: The function or callable object being decorated.

    Returns:
        A dictionary containing the qualified function name and module.
    """
    name = getattr(func, "__qualname__", getattr(func, "__name__", "callable"))
    module = getattr(func, "__module__", None)

    return {
        "name": name,
        "module": module,
    }


_DESIGN_NOTES = """
# get_context_info — log_this Metadata Extractor

## Purpose
Safely extracts human-readable function metadata (`name` and `module`) at
decoration time. Isolates defensive reflection logic and IDE inspection
warnings away from the main `@log_this` decorator and logging helpers.
"""