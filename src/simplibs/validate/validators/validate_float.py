from typing import Any, Container
# Inners
from .rules.float_rule import float_rule


def validate_float(
    value: Any,
    *,
    # Processing params:
    greater_than: float | None = None,
    greater_or_equal: float | None = None,
    less_than: float | None = None,
    less_or_equal: float | None = None,
    in_range: tuple[float, float] | None = None,
    positive: bool = False,
    negative: bool = False,
    close_to_target: float | None = None,
    close_to_rel_tol: float = 1e-9,
    close_to_abs_tol: float = 0.0,
    finite: bool = True,
    equals: float | None = None,
    not_equals: float | None = None,
    is_in: Container[Any] | None = None,
    not_in: Container[Any] | None = None,
    # Setting params:
    value_name: str | None = None,
    context: str | None = None,
    return_bool: bool = False,
    return_value: bool = False,
) -> Any:
    """Validate a value as a float against the given optional constraints.

    Thin convenience wrapper: composes float_rule(...) and immediately
    validates `value` against it via Rule.validate(). For repeated
    validation against the same constraints, build the rule once with
    float_rule(...) and reuse it directly instead of calling this
    function in a loop.

    Args:
        value: The tested value.
        greater_than: The value must be strictly greater than this threshold.
        greater_or_equal: The value must be greater than or equal to this threshold.
        less_than: The value must be strictly less than this threshold.
        less_or_equal: The value must be less than or equal to this threshold.
        in_range: (min_val, max_val) — inclusive range.
        positive: If True, the value must be strictly greater than 0.
        negative: If True, the value must be strictly less than 0.
        close_to_target: If given, the value must be approximately equal
            to this target.
        close_to_rel_tol: Relative tolerance for close_to_target.
        close_to_abs_tol: Absolute tolerance for close_to_target.
        finite: If True (default), excludes NaN and +/-Infinity.
        equals: The value must equal this exact float.
        not_equals: The value must NOT equal this exact float.
        is_in: The value must be one of the given options.
        not_in: The value must NOT be one of the given options.
        value_name: The name of the validated variable/parameter for
            diagnostic reports.
        context: Additional context describing the validation environment.
        return_bool: If True, returns False on validation failure instead
            of raising an exception.
        return_value: If validation passes and this is True, returns the
            original value instead of True.

    Returns:
        Returns `value`, `True`, or `False` depending on the specified
        parameter flags.

    Raises:
        Exception: If validation fails and `return_bool` is False.
    """
    # 1. Compose the rule, then delegate straight to Rule.validate()
    return float_rule(
        greater_than=greater_than,
        greater_or_equal=greater_or_equal,
        less_than=less_than,
        less_or_equal=less_or_equal,
        in_range=in_range,
        positive=positive,
        negative=negative,
        close_to_target=close_to_target,
        close_to_rel_tol=close_to_rel_tol,
        close_to_abs_tol=close_to_abs_tol,
        finite=finite,
        equals=equals,
        not_equals=not_equals,
        is_in=is_in,
        not_in=not_in,
    ).validate(
        value,
        value_name=value_name,
        context=context,
        return_bool=return_bool,
        return_value=return_value,
    )


_DESIGN_NOTES = """
# validate_float — Top of the Float Validation Path

See `validate_str.py`'s design notes for the shared rationale.
"""