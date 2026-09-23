import inspect
# Inners
from .BYPASS_PARAM_NAME import BYPASS_PARAM_NAME


def is_bypass_parameter(param: inspect.Parameter) -> bool:
    """True if this parameter is validate_call's reserved per-call bypass switch.

    A parameter literally named "_validate_call", with no annotation or an
    explicit `bool` annotation, is treated as a per-call opt-out rather
    than a value to validate — e.g. `def f(x: int, *, _validate_call: bool = True)`.
    A parameter named "_validate_call" with any OTHER annotation is treated as
    an ordinary parameter and validated normally (see design notes).

    Args:
        param: The inspect.Parameter being examined.

    Returns:
        True if this parameter should be excluded from rule compilation
        and instead checked at call time to skip validation entirely.
    """
    return (
        param.name == BYPASS_PARAM_NAME
        and param.annotation in (inspect.Parameter.empty, bool)
    )


_DESIGN_NOTES = """
# is_bypass_parameter — validate_call's Reserved Bypass Flag Detector

## Purpose
Lets a function opt out of validate_call's own checks on a per-call
basis — useful when a function is sometimes called directly (validation
wanted) and sometimes called from code that has already validated the
same data upstream (validation would be redundant work):

    @validate_call
    def process(data: dict, *, _validate_call: bool = True): ...

    process(data)                         # validated
    process(data, _validate_call=False)  # skipped — caller already validated

---

## 1. Detected by Name + Annotation, Not Position

An earlier design considered requiring `_validate_call` to be the last
parameter, to make it easy to locate. This was rejected: Python already
has an unambiguous, purpose-built mechanism for "this parameter is a
named switch, not positional data" — keyword-only parameters (`*,
_validate_call: bool = True`) — so position is not needed to make this
parameter identifiable or safe to call. Detecting by name is sufficient
because a parameter actually named "_validate_call" with a non-bool annotation
is vanishingly unlikely to also want bypass semantics; the annotation
check exists specifically to leave that rare, deliberate case alone
(see the type check below).

---

## 2. Annotation Escape Hatch

A function that genuinely needs a parameter named `_validate_call` for
unrelated data (not a bool) is not forced to rename it — giving it any
annotation other than `bool` (or no bypass semantics intended, an
explicit override could also be added) causes it to be treated as an
ordinary parameter, validated like any other. Only the specific
"named _validate_call, boolean or unannotated" shape triggers bypass behavior.
"""