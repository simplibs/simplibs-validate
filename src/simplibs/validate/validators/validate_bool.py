from typing import Any
# Inners
from .rules.boolean_rule import boolean_rule


def validate_bool(
    value: Any,
    *,
    # Processing params:
    equals: bool | None = None,
    # Setting params:
    value_name: str | None = None,
    context: str | None = None,
    return_bool: bool = False,
    return_value: bool = False,
) -> Any:
    """Validate a value as a boolean, optionally against a fixed expected value.

    Thin convenience wrapper: composes boolean_rule(...) and immediately
    validates `value` against it via Rule.validate(). For repeated
    validation against the same constraints, build the rule once with
    boolean_rule(...) and reuse it directly instead of calling this
    function in a loop.

    Args:
        value: The tested value.
        equals: If given, the value must equal this exact boolean.
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
    return boolean_rule(
        equals=equals
    ).validate(
        value,
        value_name=value_name,
        context=context,
        return_bool=return_bool,
        return_value=return_value,
    )


_DESIGN_NOTES = """
# validate_bool — Top of the Boolean Validation Path

See `validate_string.py`'s design notes for the shared rationale.
"""