from typing import Any, Callable, NoReturn
from simplibs.exception import ParamError


def raise_no_iterable_parameter(func: Callable[..., Any]) -> NoReturn:
    """Raise a ParamError when `materialize_iterators=True` has nothing to act on.

    Args:
        func: The function being decorated by validate_call.

    Raises:
        ParamError: Always.
    """
    raise ParamError(
        error_name="VALIDATE_CALL_NO_ITERABLE_PARAM_ERROR",
        label="materialize_iterators",
        expected="A function with at least one validated parameter annotated as Iterable[T].",
        value=True,
        problem=(
            f"{func.__qualname__}() has no validated parameter annotated as Iterable[T].",
            "The flag would never change anything.",
        ),
        how_to_fix=(
            "Annotate the parameter as Iterable[T] (for example Iterable[int]).",
            "Make sure the parameter is not excluded by the 'check' parameter list.",
            "Remove materialize_iterators=True.",
        ),
    )


_DESIGN_NOTES = """
# raise_no_iterable_parameter — validate_call Diagnostic Helper

## Purpose
Single point of failure for "materialize_iterators=True, but there is no
parameter it could apply to". Raised at decoration time, like
raise_no_rule_for_checked_param, so a flag that silently does nothing (a typo
in an annotation, a parameter dropped by `check`) is caught at import time.
"""
