import inspect
# Inners
from .is_bypass_parameter import BYPASS_PARAM_NAME


def should_validate(
    bound: inspect.BoundArguments,
    *,
    has_bypass: bool
) -> bool:
    """Whether this specific call should run validate_call's checks at all.

    Args:
        bound: This call's bound arguments (defaults already applied).
        has_bypass: Whether the decorated function has a reserved
            "validate" bypass parameter at all (see is_bypass_parameter) —
            computed once, at decoration time.

    Returns:
        True if the function has no bypass parameter (validation always
        runs), or if it does and its value for this call is truthy.
        False only when the bypass parameter is present and falsy.
    """

    # 1. No bypass parameter exists on this function — always validate
    if not has_bypass:
        return True

    # 2. Bypass parameter exists — its value for this call decides
    return bool(bound.arguments.get(BYPASS_PARAM_NAME, True))


_DESIGN_NOTES = """
# should_validate — validate_call's Per-Call Bypass Check

## Purpose
Decides, for one specific call, whether validate_call's checks should run
at all. Kept as its own pure function (bound arguments + a precomputed
flag in, bool out) rather than a closure inside validate_call's wrapper,
so it can be tested directly against a constructed BoundArguments without
going through the decorator machinery.

---

## 1. Why This Cannot Be Resolved at Decoration Time

`has_bypass` (does this function even have a "validate" parameter) is a
structural fact about the function's signature — knowable once, when the
decorator is applied. But the *value* passed for that parameter on any
given call — True, False, or its default — depends on that call's actual
arguments, which do not exist until `bound = signature.bind(*args,
**kwargs)` runs inside the wrapper. This function is therefore
necessarily called once per invocation, never memoized alongside
`has_bypass` itself.

---

## 2. Default Is `True` When the Parameter Wasn't Explicitly Bound

`bound.arguments.get(BYPASS_PARAM_NAME, True)` — if the bypass parameter
has a default and the caller didn't override it, `bound.apply_defaults()`
(called by the wrapper before this function runs) already puts that
default into `bound.arguments`, so the `True` fallback here only matters
in the (currently unreachable, since has_bypass already confirmed the
parameter exists) case of a missing entry. Kept as a safe default rather
than assuming the key is always present, in case `has_bypass` and this
function's underlying assumptions ever drift apart in a future change.
"""