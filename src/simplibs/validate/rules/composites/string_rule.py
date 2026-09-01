from simplibs.sentinels import UNSET, UnsetType
from ..base_class import Rule
from ..containers import AllOf
from .. import (
    is_string, has_length, starts_with, ends_with,
    contains, regex, not_blank, equals, not_equals,
    is_in, not_in,
)


def string_rule(
    *,
    min_length: int | UnsetType = UNSET,
    max_length: int | UnsetType = UNSET,
    length: int | UnsetType = UNSET,
    starts_with_: str | UnsetType = UNSET,
    ends_with_: str | UnsetType = UNSET,
    contains_: str | UnsetType = UNSET,
    pattern: str | UnsetType = UNSET,
    blank: bool = True,  # False => vyžaduje not_blank
    equals_: str | UnsetType = UNSET,
    not_equals_: str | UnsetType = UNSET,
    is_in_: tuple | UnsetType = UNSET,
    not_in_: tuple | UnsetType = UNSET,
) -> Rule:
    """Compose a Rule validating a string against the given optional constraints."""
    parts: list[Rule] = [is_string]

    if length is not UNSET:
        parts.append(has_length(length=length))
    else:
        if min_length is not UNSET or max_length is not UNSET:
            kwargs = {}
            if min_length is not UNSET:
                kwargs["min_length"] = min_length
            if max_length is not UNSET:
                kwargs["max_length"] = max_length
            parts.append(has_length(**kwargs))

    if starts_with_ is not UNSET:
        parts.append(starts_with(starts_with_))
    if ends_with_ is not UNSET:
        parts.append(ends_with(ends_with_))
    if contains_ is not UNSET:
        parts.append(contains(contains_))
    if pattern is not UNSET:
        parts.append(regex(pattern))
    if not blank:
        parts.append(not_blank)
    if equals_ is not UNSET:
        parts.append(equals(equals_))
    if not_equals_ is not UNSET:
        parts.append(not_equals(not_equals_))
    if is_in_ is not UNSET:
        parts.append(is_in(is_in_))
    if not_in_ is not UNSET:
        parts.append(not_in(not_in_))

    return AllOf(*parts) if len(parts) > 1 else parts[0]


def validate_string(value, **kwargs):
    from ..validate import validate
    return_bool = kwargs.pop("return_bool", False)
    return_value = kwargs.pop("return_value", False)
    return validate(
        value, string_rule(**kwargs),
        return_bool=return_bool, return_value=return_value,
    )