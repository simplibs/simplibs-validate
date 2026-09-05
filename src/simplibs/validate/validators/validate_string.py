from typing import Any, Container
# Inners
from .rules.string_rule import string_rule


def validate_string(
    value: Any,
    *,
    # Processing params:
    min_length: int | None = None,
    max_length: int | None = None,
    length: int | None = None,
    starts_with: str | None = None,
    ends_with: str | None = None,
    contains: str | None = None,
    is_substring_of: str | None = None,
    regex_search: str | None = None,
    is_blank: bool | None = None,
    equals: str | None = None,
    not_equals: str | None = None,
    is_in: Container[Any] | None = None,
    not_in: Container[Any] | None = None,
    # Setting params:
    value_name: str | None = None,
    context: str | None = None,
    return_bool: bool = False,
    return_value: bool = False,
) -> Any:
    """Validate a value as a string against the given optional constraints.

    Thin convenience wrapper: composes string_rule(...) and immediately
    validates `value` against it via Rule.validate(). For repeated
    validation against the same constraints, build the rule once with
    string_rule(...) and reuse it directly instead of calling this
    function in a loop.

    Args:
        value: The tested value.
        min_length: Minimum allowed length. Ignored if `length` is also given.
        max_length: Maximum allowed length. Ignored if `length` is also given.
        length: Exact required length. Conflicts with min_length/max_length
            (raises ParamError).
        starts_with: Required prefix.
        ends_with: Required suffix.
        contains: Required substring.
        is_substring_of: Target string in which the evaluated string must be contained.
        regex_search: Required regular expression pattern, matched anywhere
            in the string via `re.search`.
        is_blank: If None (default), blankness is unconstrained. If True, the
            string must be blank. If False, the string must NOT be blank.
        equals: The value must equal this exact string.
        not_equals: The value must NOT equal this exact string.
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
    return string_rule(
        min_length=min_length,
        max_length=max_length,
        length=length,
        starts_with=starts_with,
        ends_with=ends_with,
        contains=contains,
        is_substring_of=is_substring_of,
        regex_search=regex_search,
        is_blank=is_blank,
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
# validate_string — Top of the String Validation Path

## Purpose
The final step of the string / string_rule / validate_string chain: a
full-featured, standalone entry point for one-off string validation,
carrying the same completeness of interface as calling `.validate()` on
any hand-built Rule directly.

---

## 1. Direct `.validate()` Delegation, Not the `validate()` Function

Calls `string_rule(...).validate(value, ...)` directly rather than routing
through the top-level `validate()` function. `validate()` exists to bridge
two possible inputs (a `Rule` instance or a plain callable); here the
input is always and only a `Rule` — the one this module just built — so
that bridging logic has nothing to do and is skipped entirely.

---

## 2. Full Parameter Surface, Not a Reduced One

Unlike a minimal pass-through, this function's docstring documents every
parameter `Rule.validate()` accepts (`value_name`, `context`,
`return_bool`, `return_value`) alongside every constraint `string_rule`
accepts. As the outermost public entry point on this path, it is expected
to be fully self-documenting on its own, without sending the caller back
to `string_rule` or `Rule.validate` to understand its signature.
"""