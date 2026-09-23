import inspect
from typing import Any, Callable


def unwrap_log_this(
    func: Callable[..., Any]
) -> Callable[..., Any]:
    """Recursively strip existing @log_this wrapper layers from a callable.

    Unwraps functions decorated with @log_this until a non-log_this layer
    (or the underlying raw function) is reached. Preserves non-log_this
    decorators (such as @cache, @retry, or custom decorators) that do not
    set `_is_log_this_wrapper = True`.

    Args:
        func: The target function or callable object to unwrap.

    Returns:
        The underlying function with any @log_this wrappers removed.
    """

    # 1. Initialize iteration pointer with the provided function
    current = func

    # 2. Traverse wrapper layers while the current function is marked as a @log_this wrapper
    while getattr(current, "_is_log_this_wrapper", False):

        # 2.1 Extract underlying wrapped callable via __wrapped__ attribute
        wrapped = getattr(current, "__wrapped__", None)

        # 2.2 Break traversal if __wrapped__ reference is missing or broken
        if wrapped is None:
            break

        # 2.3 Move to the next inner function layer
        current = wrapped

    # 3. Return the clean function stripped of all @log_this wrappers
    return current


_DESIGN_NOTES = """
# unwrap_log_this — Selective Log This Wrapper Stripper

## Purpose
Enables `@log_this` to detect and strip prior `@log_this` decoration layers
before inspecting signatures or compiling logging context.

---

## 1. Targeted Unwrapping via Explicit Marker

Unlike `inspect.unwrap`, which indiscriminately strips all `__wrapped__`
attributes until it reaches the raw function (removing useful decorators like
`@cache` or custom wrappers in the process), `unwrap_log_this` specifically
looks for `_is_log_this_wrapper = True`.

---

## 2. Prevention of Redundant Logging

When multiple `@log_this` decorators are accidentally stacked or reapplied
dynamically, peeling off prior layers prevents duplicate log records and
overlapping execution timers for a single function invocation.
"""