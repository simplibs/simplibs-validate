from typing import Any


def get_dataclass_context_string(cls: type[Any]) -> str:
    """Extract a human-readable dataclass execution context string.

    Args:
        cls: The dataclass type being decorated.

    Returns:
        A formatted string describing the dataclass's module and qualified name
        for diagnostic exception messaging.
    """
    cls_name = getattr(cls, "__qualname__", getattr(cls, "__name__", "dataclass"))
    cls_module = getattr(cls, "__module__", None)

    if cls_module:
        return f"Dataclass {cls_module}.{cls_name}"
    return f"Dataclass {cls_name}"


_DESIGN_NOTES = """
# get_dataclass_context_string — validate_dataclass Context Builder

## Purpose
Safely extracts human-readable diagnostic metadata (`__module__` and `__qualname__`)
from target dataclass types at decoration time. Formats execution context as 
"Dataclass module.Name" (rather than "Function ...") to provide intuitive, 
type-accurate error messaging during instance construction.
"""