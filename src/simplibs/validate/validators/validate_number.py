from typing import Any, Container
# Inners
from .rules.number_rule import number_rule


def validate_number(
    value: Any,
    *,
    # Processing params:
    greater_than: Any | None = None,
    greater_or_equal: Any | None = None,
    less_than: Any | None = None,
    less_or_equal: Any | None = None,
    in_range: tuple[Any, Any] | None = None,
    positive: bool = False,
    negative: bool = False,
    equals: Any | None = None,
    not_equals: Any | None = None,
    is_in: Container[Any] | None = None,
    not_in: Container[Any] | None = None,
    # Setting params:
    value_name: str | None = None,
    context: str | None = None,
    return_bool: bool = False,
    return_value: bool = False,
) -> Any:
    """Validate a value as a number against the given optional constraints.

    Thin convenience wrapper: composes number_rule(...) and immediately
    validates `value` against it via Rule.validate(). For repeated
    validation against the same constraints, build the rule once with
    number_rule(...) and reuse it directly instead of calling this
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
        equals: The value must equal this exact number.
        not_equals: The value must NOT equal this exact number.
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
    return number_rule(
        greater_than=greater_than,
        greater_or_equal=greater_or_equal,
        less_than=less_than,
        less_or_equal=less_or_equal,
        in_range=in_range,
        positive=positive,
        negative=negative,
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
# validate_number — Top of the General Number Validation Path

See `validate_string.py`'s design notes for the shared rationale.
"""