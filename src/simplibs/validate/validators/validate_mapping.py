from typing import Any
from simplibs.sentinels import UNSET, UnsetType
# Inners
from .rules.mapping_rule import mapping_rule


def validate_mapping(
    value: Any,
    *,
    # Processing params:
    min_length: int | None = None,
    max_length: int | None = None,
    length: int | None = None,
    has_key: Any | UnsetType = UNSET,
    has_keys: tuple[Any, ...] | None = None,
    # Setting params:
    value_name: str | None = None,
    context: str | None = None,
    return_bool: bool = False,
    return_value: bool = False,
) -> Any:
    """Validate a value as a dict against the given optional constraints.

    Thin convenience wrapper: composes mapping_rule(...) and immediately
    validates `value` against it via Rule.validate(). For repeated
    validation against the same constraints, build the rule once with
    mapping_rule(...) and reuse it directly instead of calling this
    function in a loop.

    Args:
        value: The tested value.
        min_length: Minimum allowed number of entries. Ignored if `length` is also given.
        max_length: Maximum allowed number of entries. Ignored if `length` is also given.
        length: Exact required number of entries. Conflicts with min_length/max_length.
        has_key: If given, the value must contain this single key. Uses
            the UNSET sentinel, since None is itself a valid dict key.
        has_keys: If given, the value must contain all of these keys.
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
    return mapping_rule(
        min_length=min_length,
        max_length=max_length,
        length=length,
        has_key=has_key,
        has_keys=has_keys,
    ).validate(
        value,
        value_name=value_name,
        context=context,
        return_bool=return_bool,
        return_value=return_value,
    )


_DESIGN_NOTES = """
# validate_mapping — Top of the Mapping Validation Path

See `validate_str.py`'s design notes for the shared rationale. Note
that `has_key` keeps the `UNSET` sentinel here too, for the same reason
documented in `mapping_rule.py`.
"""