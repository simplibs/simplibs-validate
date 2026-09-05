from typing import Any, Container
# Inners
from .rules.type_rule import type_rule


def validate_type(
    value: Any,
    *,
    # Processing params:
    subclass_of: tuple[type, ...] | None = None,
    equals: type | None = None,
    not_equals: type | None = None,
    is_in: Container[type] | None = None,
    not_in: Container[type] | None = None,
    # Setting params:
    value_name: str | None = None,
    context: str | None = None,
    return_bool: bool = False,
    return_value: bool = False,
) -> Any:
    """Validate a value as a class/type object against the given optional constraints.

    Thin convenience wrapper: composes type_rule(...) and immediately
    validates `value` against it via Rule.validate(). For repeated
    validation against the same constraints, build the rule once with
    type_rule(...) and reuse it directly instead of calling this function
    in a loop.

    Args:
        value: The tested value.
        subclass_of: If given, the value must be a subclass of one or more
            of these base classes. Given as a tuple even for a single
            base class.
        equals: The value must equal (be identical to) this exact class.
        not_equals: The value must NOT equal this exact class.
        is_in: The value must be one of the given classes.
        not_in: The value must NOT be one of the given classes.
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
    return type_rule(
        subclass_of=subclass_of,
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
# validate_type — Top of the Type/Class Validation Path

See `validate_string.py`'s design notes for the shared rationale.
"""