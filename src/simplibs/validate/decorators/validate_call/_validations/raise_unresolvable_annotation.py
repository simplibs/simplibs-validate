from typing import Any, Callable, NoReturn
from simplibs.exception import ParamError


def raise_unresolvable_annotation(func: Callable[..., Any], error: Exception) -> NoReturn:
    """Raise a ParamError when a string annotation cannot be evaluated.

    Args:
        func: The function (or dataclass __init__) whose annotations failed.
        error: The exception raised while evaluating them (usually NameError).

    Raises:
        ParamError: Always, chained from `error`.
    """
    raise ParamError(
        error_name="VALIDATE_CALL_UNRESOLVABLE_ANNOTATION_ERROR",
        label=func.__qualname__,
        expected="Annotations whose names exist in the module of the function when it is first called.",
        value=f"{type(error).__name__}: {error}",
        problem=(
            f"The annotations of {func.__qualname__}() could not be resolved.",
            f"Evaluating them failed with {type(error).__name__}: {error}",
        ),
        how_to_fix=(
            "Import the name at module level (not only under TYPE_CHECKING).",
            "Define the referenced class at module level, not inside another function.",
            "Check the annotation for a typo.",
            "Use a real object instead of a string, or drop the annotation and use 'overrides'.",
        ),
    ) from error


_DESIGN_NOTES = """
# raise_unresolvable_annotation — validate_call Diagnostic Helper

## Purpose
Single point of failure for annotations that cannot be turned into real
objects: a name that does not exist (even at the first call), or a string that
is not valid annotation syntax. The original exception stays attached as the
cause, so the traceback still shows exactly what failed to evaluate.
"""
