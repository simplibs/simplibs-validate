from typing import Any, Callable, Collection
from simplibs.rules import Rule
# Inners
from .rules.container_rule import container_rule


def validate_container(
    value: Any,
    *,
    # Processing params:
    min_length: int | None = None,
    max_length: int | None = None,
    length: int | None = None,
    unique: bool = False,
    has_item: Any | None = None,
    subset_of: Collection[Any] | None = None,
    superset_of: Collection[Any] | None = None,
    for_each: Rule | Callable[[Any], bool] | None = None,
    # Setting params:
    value_name: str | None = None,
    context: str | None = None,
    return_bool: bool = False,
    return_value: bool = False,
) -> Any:
    """Validate a value as a container against the given optional constraints.

    Thin convenience wrapper: composes container_rule(...) and immediately
    validates `value` against it via Rule.validate(). For repeated
    validation against the same constraints, build the rule once with
    container_rule(...) and reuse it directly instead of calling this
    function in a loop.

    Args:
        value: The tested value.
        min_length: Minimum allowed number of items. Ignored if `length` is also given.
        max_length: Maximum allowed number of items. Ignored if `length` is also given.
        length: Exact required number of items. Conflicts with min_length/max_length.
        unique: If True, every item in the container must be unique.
        has_item: If given, the value must contain this single item.
        subset_of: If given, every item in the value must appear in this
            reference collection.
        superset_of: If given, every item in this reference collection
            must appear in the value.
        for_each: If given, every item in the value must satisfy this rule
            or callable.
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
    return container_rule(
        min_length=min_length,
        max_length=max_length,
        length=length,
        unique=unique,
        has_item=has_item,
        subset_of=subset_of,
        superset_of=superset_of,
        for_each=for_each,
    ).validate(
        value,
        value_name=value_name,
        context=context,
        return_bool=return_bool,
        return_value=return_value,
    )


_DESIGN_NOTES = """
# validate_container — Top of the Container Validation Path

See `validate_str.py`'s design notes for the shared rationale (direct
`.validate()` delegation instead of the `validate()` function, full
parameter surface documented at this outermost layer).
"""