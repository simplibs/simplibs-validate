from typing import Any, Callable, NoReturn
# Outers
from ....exceptions import ParamError


def raise_no_rule_for_return(func: Callable[..., Any]) -> NoReturn:
    """Raise a ParamError when check_return=True is given but there is no
    return annotation to validate against.

    Args:
        func: The function being decorated by validate_call.

    Raises:
        ParamError: Always.
    """
    raise ParamError(
        error_name="VALIDATE_CALL_NO_RULE_FOR_RETURN_ERROR",
        label="check_return",
        expected="A function with an explicit return type annotation.",
        value=func.__qualname__,
        problem=(
            f"Option 'check_return=True' was enabled for function {func.__qualname__}().",
            "The function does not define a return type annotation ('-> ...') to validate against.",
        ),
        how_to_fix=(
            f"Add a return type annotation to function {func.__qualname__}().",
            "Disable return validation by removing 'check_return=True'.",
        ),
    )


_DESIGN_NOTES = """
# raise_no_rule_for_return — validate_call Diagnostic Helper

## Purpose
Single point of failure for the "check_return was requested, but there is
no return annotation to validate against" case. Mirrors
raise_no_rule_for_checked_param's rationale, applied to the return value
instead of a parameter — an explicit request for a check that has no
rule source behind it is always an error, never a silent no-op. See
validate_call's own design notes for the parameter-side equivalent this
mirrors.
"""