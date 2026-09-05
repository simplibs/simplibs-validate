from typing import Any, Callable, NoReturn
# Outers
from ....exceptions import ParamError


def raise_no_rule_for_checked_param(
    func: Callable[..., Any],
    name: str
) -> NoReturn:
    """Raise a ParamError when `check` names a parameter with no rule source.

    Args:
        func: The function being decorated by validate_call.
        name: The parameter name listed in `check` that has neither a
            type annotation nor an `overrides` entry.

    Raises:
        ParamError: Always.
    """
    raise ParamError(
        error_name="VALIDATE_CALL_NO_RULE_FOR_PARAM_ERROR",
        label="check",
        expected="A parameter with a type annotation or an entry in overrides.",
        value=name,
        problem=(
            f"Parameter '{name}' of {func.__qualname__}() was listed in 'check'.",
            "The parameter has neither a type annotation nor a custom override rule.",
        ),
        how_to_fix=(
            f"Add a type annotation to parameter '{name}'.",
            f"Provide an explicit rule entry: overrides={{'{name}': ...}}.",
            f"Remove '{name}' from the 'check' parameter list.",
        ),
    )


_DESIGN_NOTES = """
# raise_no_rule_for_checked_param — validate_call Diagnostic Helper

## Purpose
Single point of failure for the "check named a parameter, but nothing
exists to validate it against" case — raised at decoration time, not on
first call, so the mistake surfaces at import time rather than at some
later, possibly production, call site. See validate_call's own design
notes, section 4, for the full rationale on why this is an error rather
than a silent skip.
"""