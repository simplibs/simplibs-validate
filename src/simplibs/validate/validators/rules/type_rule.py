from typing import Any, Container
from simplibs.rules import (
    Rule,
    AllOf,
    is_type as _is_type,
    is_subclass as _is_subclass,
    equals as _equals,
    not_equals as _not_equals,
    is_in as _is_in,
    not_in as _not_in,
)


def type_rule(
    *,
    subclass_of: tuple[type, ...] | None = None,
    equals: type | None = None,
    not_equals: type | None = None,
    is_in: Container[type] | None = None,
    not_in: Container[type] | None = None,
) -> Rule:
    """Compose a Rule validating a class/type object against the given optional constraints.

    Args:
        subclass_of: If given, the value must be a subclass of one or more
            of these base classes (IsSubclass). Given as a tuple even for
            a single base class, e.g. `subclass_of=(BaseClass,)`.
        equals: The value must equal (be identical to) this exact class.
        not_equals: The value must NOT equal this exact class.
        is_in: The value must be one of the given classes.
        not_in: The value must NOT be one of the given classes.

    Returns:
        A single Rule instance — `is_type` itself if no constraint is
        given, otherwise an AllOf combining the type-object check with
        every given constraint.
    """
    # 1. Base type-object check
    parts: list[Rule] = [_is_type]

    # 2. Inheritance
    if subclass_of is not None:
        parts.append(_is_subclass(*subclass_of))

    # 3. Exact equality
    if equals is not None:
        parts.append(_equals(equals))

    # 4. Exact inequality
    if not_equals is not None:
        parts.append(_not_equals(not_equals))

    # 5. Membership
    if is_in is not None:
        parts.append(_is_in(is_in))

    # 6. Non-membership
    if not_in is not None:
        parts.append(_not_in(not_in))

    # 7. Collapse to a single Rule
    return (
        AllOf(*parts)
        if len(parts) > 1
        else parts[0]
    )


_DESIGN_NOTES = """
# type_rule — Composed Type/Class Object Validation Rule

## Purpose
Layer-3 composition over `IsType` (layer 1) / `is_type` (layer 2) — for
validating that a value is itself a class object (not an instance), with
optional inheritance and identity constraints. See `string_rule.py`'s
design notes for the shared pattern.

---

## 1. `subclass_of` Always Takes a Tuple, Even for One Base Class

`IsSubclass(*types)` is variadic. Since this composed layer exposes it as
one keyword parameter, `subclass_of` is always a tuple
(`subclass_of=(BaseClass,)` for a single base) and unpacked with
`*subclass_of` when building `IsSubclass`. This differs from `is_in`/
`not_in`, which also accept a container but pass it through to
`IsIn`/`NotIn` as a single argument rather than unpacking — the
distinction follows each underlying rule's own constructor signature.

---

## 2. Redundancy With `IsSubclass` Itself

`type_rule(subclass_of=(BaseClass,))` composes to `AllOf(IsType(),
IsSubclass(BaseClass))`. `IsSubclass.is_valid` already internally checks
`isinstance(value, type)` before calling `issubclass()`, so the leading
`IsType()` is technically redundant when `subclass_of` is given. It is
kept anyway: it keeps this composed rule's base predicate consistent
regardless of which constraints are given, and it produces a clearer,
dedicated diagnostic ("this is an instance, not a class") as the first
failure reported when the value isn't a class at all.
"""