from typing import Container, Any
from simplibs.sentinels import UNSET, UnsetType
from ..base_class import Rule
from ..containers import AllOf
from ..predicates.strings import IsString, StartsWith, EndsWith, Contains, Regex, NotBlank
from ..predicates.introspection import HasLength
from ..predicates.comparisons import Equals, NotEquals
from ..predicates.logic import IsIn, NotIn


def string_rule(
    *,
    min_length: int | UnsetType = UNSET,
    max_length: int | UnsetType = UNSET,
    length: int | UnsetType = UNSET,
    starts_with: str | UnsetType = UNSET,
    ends_with: str | UnsetType = UNSET,
    contains: str | UnsetType = UNSET,
    pattern: str | UnsetType = UNSET,
    blank: bool = True,  # False => vyžaduje not_blank
    equals: str | UnsetType = UNSET,
    not_equals: str | UnsetType = UNSET,
    is_in: Container[Any] | UnsetType = UNSET,
    not_in: Container[Any] | UnsetType = UNSET,
) -> Rule:
    """Compose a Rule validating a string against the given optional constraints."""

    # 1. Validace instance
    parts: list[Rule] = [IsString()]

    # 2. Validace délky
    if length is not UNSET:
        parts.append(HasLength(length))
    else:
        if min_length is not UNSET or max_length is not UNSET:
            kwargs = {}
            if min_length is not UNSET:
                kwargs["min_length"] = min_length
            if max_length is not UNSET:
                kwargs["max_length"] = max_length
            parts.append(HasLength(**kwargs))

    # 3.
    if starts_with is not UNSET:
        parts.append(StartsWith(starts_with))

    # 4.
    if ends_with is not UNSET:
        parts.append(EndsWith(ends_with))

    # 5.
    if contains is not UNSET:
        parts.append(Contains(contains))

    # 6.
    if pattern is not UNSET:
        parts.append(Regex(pattern))

    # 7.
    if not blank:
        parts.append(NotBlank())

    # 8.
    if equals is not UNSET:
        parts.append(Equals(equals))

    # 9.
    if not_equals is not UNSET:
        parts.append(NotEquals(not_equals))

    # 10.
    if is_in is not UNSET:
        parts.append(IsIn(is_in))

    # 11.
    if not_in is not UNSET:
        parts.append(NotIn(not_in))

    # 12. Navrácení sestaveného pravidla
    return AllOf(*parts) if len(parts) > 1 else parts[0]


def validate_string(
    value,
    *,
    min_length: int | UnsetType = UNSET,
    max_length: int | UnsetType = UNSET,
    length: int | UnsetType = UNSET,
    starts_with: str | UnsetType = UNSET,
    ends_with: str | UnsetType = UNSET,
    contains: str | UnsetType = UNSET,
    pattern: str | UnsetType = UNSET,
    blank: bool = True,  # False => vyžaduje not_blank
    equals: str | UnsetType = UNSET,
    not_equals: str | UnsetType = UNSET,
    is_in: tuple | UnsetType = UNSET,
    not_in: tuple | UnsetType = UNSET,

    value_name: str | None = None,
    context: str | None = None,
    return_bool: bool = False,
    return_value: bool = False,
):
    return string_rule(
        min_length=min_length,
        max_length=max_length,
        length=length,
        starts_with=starts_with,
        ends_with=ends_with,
        contains=contains,
        pattern=pattern,
        blank=blank,
        equals=equals,
        not_equals=not_equals,
        is_in=is_in,
        not_in=not_in,
    ).validate(
        value=value,
        value_name=value_name,
        context=context,
        return_bool=return_bool,
        return_value=return_value,
    )

    # from ...validate import validate
    #
    # return validate(
    #     value,
    #     string_rule(
    #         min_length=min_length,
    #         max_length=max_length,
    #         length=length,
    #         starts_with=starts_with,
    #         ends_with=ends_with,
    #         contains=contains,
    #         pattern=pattern,
    #         blank=blank,
    #         equals=equals,
    #         not_equals=not_equals,
    #         is_in=is_in,
    #         not_in=not_in,
    #     ),
    #     value_name=value_name,
    #     context=context,
    #     return_bool=return_bool,
    #     return_value=return_value,
    # )