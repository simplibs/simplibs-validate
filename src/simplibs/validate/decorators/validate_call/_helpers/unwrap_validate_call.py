from typing import Any, Callable


def unwrap_validate_call(
    func: Callable[..., Any]
) -> Callable[..., Any]:
    """Recursively peel off any existing @validate_call wrappers from a callable.

    Traverses the `__wrapped__`/`__func__` chain as long as the current
    layer presents the `_is_validate_call_wrapper = True` marker set by
    validate_call. Other wrappers (e.g., custom decorators, `@cache`,
    `@retry`) that do not originate from `@validate_call` are preserved
    intact.

    Args:
        func: The decorated function or callable to unwrap.

    Returns:
        The underlying function with all `@validate_call` decorator layers removed.
    """

    # 1. Initialize traversal with the input callable
    current = func

    # 2. Iterate while the current function layer carries the @validate_call marker
    while getattr(current, "_is_validate_call_wrapper", False):

        # 2.1 Prefer __wrapped__ (the standard functools.wraps target)
        next_layer = getattr(current, "__wrapped__", None)

        # 2.2 Fall back to __func__ for layers without __wrapped__
        #     (e.g. bound/unbound method wrappers, some descriptor objects)
        if next_layer is None:
            next_layer = getattr(current, "__func__", None)

        # 2.3 Neither attribute exists — stop here rather than loop forever
        if next_layer is None:
            break

        # 2.4 Descend to the next inner layer
        current = next_layer

    # 3. Return the fully unwrapped function without @validate_call layers
    return current


_DESIGN_NOTES = """
# unwrap_validate_call — Selective validate_call Unwrap Helper

## Purpose
Strips away previous `@validate_call` wrapper layers from a given function,
preventing duplicate validation runs and redundant type checks when a function
is decorated multiple times or passed through validation-enabled factory
pipelines (such as `create_action`).

---

## 1. Surgical Unwrapping vs. `inspect.unwrap`

Standard `inspect.unwrap` blindly strips all `__wrapped__` layers until it
reaches the innermost function. This would erroneously strip essential
user-level decorators like `@cache`, `@retry`, or custom domain decorators.
By checking for `_is_validate_call_wrapper = True`, this helper selectively
peels off *only* `@validate_call` layers, keeping all other functional
wrappers intact.

---

## 2. Decoupled and Modular Design

This helper isolates the unwrapping traversal logic away from `validate_call`'s
main body and compilation pipelines. It operates purely on python object
reflection and attribute inspection, ensuring no circular imports or side
effects occur during decoration time.

---

## 3. Fallback Sequence — Corrected to Actually Terminate

Each loop iteration resolves the next layer in three explicit, sequential
steps: try `__wrapped__` first (the standard `functools.wraps` target);
if absent, try `__func__` (for bound/unbound method wrappers or specific
descriptor objects that don't set `__wrapped__`); if *neither* is
present, `break` immediately.

An earlier version of this helper wrote that fallback as a single nested
expression — `getattr(current, "__wrapped__", getattr(current, "__func__", current))`
— falling back to `current` itself when neither attribute existed. That
is the opposite of safe: if an object ever carried
`_is_validate_call_wrapper = True` without either `__wrapped__` or
`__func__` (precisely the "custom wrapper class" case the old comment
cited as the reason for the fallback), `current = current` would leave
the loop condition unchanged and the `while` would never terminate. The
explicit `break` above is what actually delivers the "guaranteed safety"
the old comment claimed but did not provide.
"""
