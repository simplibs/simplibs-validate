import inspect
from typing import Any, Callable, TypeVar
# Inners
from .resolve_signature import resolve_signature
# Annotations
T = TypeVar("T")

_PENDING: Any = object()


def lazy_signature_state(
    func: Callable[..., Any],
    build: Callable[[inspect.Signature], T],
) -> Callable[[], T]:
    """Build state from the resolved signature now if possible, otherwise later.

    Args:
        func: The function (or dataclass __init__) to resolve.
        build: Receives the resolved signature and returns whatever the
            caller needs (compiled rules, ...).

    Returns:
        A getter. The first call returns the state built at decoration time,
        or builds it now when a referenced name did not exist yet; later
        calls return the same cached object.

    Raises:
        ParamError: From `build` — at decoration time when the signature is
            resolvable, otherwise on the first call. Also when a name is
            still missing on that first call.
    """

    signature = resolve_signature(func)
    state: Any = build(signature) if signature is not None else _PENDING

    def get_state() -> T:
        nonlocal state
        if state is _PENDING:
            state = build(resolve_signature(func, strict=True))
        return state

    return get_state


_DESIGN_NOTES = """
# lazy_signature_state — Build at Decoration Time, or at the First Call

## Purpose
A decorator runs while its module is still being executed, so a name used in
an annotation may not exist yet (a method annotated with its own class, a
class defined below the function). This helper keeps the early, loud failure
for everything that can be known immediately and postpones only what cannot.

---

## 1. Same Behavior as Before When Everything Resolves

Without unresolved names the state is built right away, so configuration
errors (`check` naming an unannotated parameter, ...) are still raised when the
decorator is applied.

---

## 2. Postponed Case

If a name is missing, building waits for the first call and the result is
cached. Configuration errors of that function are then raised on that first
call instead. A name that is still missing then is reported by
raise_unresolvable_annotation.

---

## 3. No Locking

Two threads making the first call at the same moment may both build the state;
the results are identical, so the last assignment simply wins.
"""
