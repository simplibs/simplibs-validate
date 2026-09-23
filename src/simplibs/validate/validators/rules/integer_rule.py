from typing import Any, Container
from simplibs.rules import (
    Rule,
    AllOf,
    is_integer as _is_integer,
    greater_than as _greater_than,
    greater_or_equal as _greater_or_equal,
    less_than as _less_than,
    less_or_equal as _less_or_equal,
    in_range as _in_range,
    divisible_by as _divisible_by,
    has_remainder as _has_remainder,
    equals as _equals,
    not_equals as _not_equals,
    is_in as _is_in,
    not_in as _not_in,
)


def integer_rule(
    *,
    greater_than: int | None = None,
    greater_or_equal: int | None = None,
    less_than: int | None = None,
    less_or_equal: int | None = None,
    in_range: tuple[int, int] | None = None,
    positive: bool = False,
    negative: bool = False,
    divisible_by: int | None = None,
    has_remainder: tuple[int, int] | None = None,
    equals: int | None = None,
    not_equals: int | None = None,
    is_in: Container[Any] | None = None,
    not_in: Container[Any] | None = None,
) -> Rule:
    """Compose a Rule validating an integer against the given optional constraints.

    Args:
        greater_than: The value must be strictly greater than this threshold.
        greater_or_equal: The value must be greater than or equal to this threshold.
        less_than: The value must be strictly less than this threshold.
        less_or_equal: The value must be less than or equal to this threshold.
        in_range: (min_val, max_val) — the value must fall within this
            inclusive range. For custom bound inclusivity, use InRange
            directly instead.
        positive: If True, the value must be strictly greater than 0
            (shortcut for greater_than=0). Combining with `negative=True`
            is a contradiction and will make the composed rule always
            fail — no dedicated guard prevents this, since a rule that
            always fails is not itself invalid, just unhelpful.
        negative: If True, the value must be strictly less than 0
            (shortcut for less_than=0).
        divisible_by: The value must be evenly divisible by this divisor.
        has_remainder: (divisor, remainder) — the value must have exactly
            this remainder when divided by divisor.
        equals: The value must equal this exact integer.
        not_equals: The value must NOT equal this exact integer.
        is_in: The value must be one of the given options.
        not_in: The value must NOT be one of the given options.

    Returns:
        A single Rule instance — `is_integer` itself if no constraint is
        given, otherwise an AllOf combining the type check with every
        given constraint.
    """
    # 1. Base type check
    parts: list[Rule] = [_is_integer]

    # 2. Sign shortcuts
    if positive:
        parts.append(_greater_than(0))
    if negative:
        parts.append(_less_than(0))

    # 3. Comparisons
    if greater_than is not None:
        parts.append(_greater_than(greater_than))
    if greater_or_equal is not None:
        parts.append(_greater_or_equal(greater_or_equal))
    if less_than is not None:
        parts.append(_less_than(less_than))
    if less_or_equal is not None:
        parts.append(_less_or_equal(less_or_equal))
    if in_range is not None:
        min_val, max_val = in_range
        parts.append(_in_range(min_val, max_val))

    # 4. Divisibility
    if divisible_by is not None:
        parts.append(_divisible_by(divisible_by))
    if has_remainder is not None:
        divisor, remainder_val = has_remainder
        parts.append(_has_remainder(divisor, remainder_val))

    # 5. Identity / membership
    if equals is not None:
        parts.append(_equals(equals))
    if not_equals is not None:
        parts.append(_not_equals(not_equals))
    if is_in is not None:
        parts.append(_is_in(is_in))
    if not_in is not None:
        parts.append(_not_in(not_in))

    # 6. Collapse to a single Rule
    return (
        AllOf(*parts)
        if len(parts) > 1
        else parts[0]
    )


_DESIGN_NOTES = """
# integer_rule — Composed Integer Validation Rule

## Purpose
Layer-3 composition over `IsInteger` (layer 1) / `is_integer` (layer 2),
covering the common numeric-comparison and divisibility constraints in
one call. See `string_rule.py`'s design notes for the shared pattern.

---

## 1. `positive` / `negative` as Flags, Not Rule Classes

`IsPositive`/`IsNegative` were deliberately **not** added as new `Rule`
subclasses. "Positive" is ambiguous in ordinary usage (does it include
zero?), and baking one interpretation into a permanent library-wide class
would silently decide that for every caller. Here, `positive=True` is
unambiguous sugar for exactly `GreaterThan(0)` (strict), scoped to this
one composition call — a caller wanting the zero-inclusive reading uses
`greater_or_equal=0` directly.

Like `unique` in `container_rule`, `positive`/`negative` are real `bool`
flags (`False` is a fully meaningful default), not `None`-sentinel
parameters — there is no ambiguity to guard against here.

* **No Guard Against `positive=True, negative=True`:** composes to a rule
  that can never pass for any integer. Detecting "this combination of
  constraints is mutually exclusive" in general is out of scope — e.g.
  `greater_or_equal=10, less_than=5` is exactly as contradictory and just
  as unguarded.

---

## 2. `in_range` Takes a Plain Tuple, Not `InRange`'s Own Signature

`InRange` supports configurable bound inclusivity. `in_range=(min_val,
max_val)` here only ever produces the default inclusive-inclusive range —
a deliberate simplification for the common case. A caller needing custom
inclusivity composes `in_range(min_val, max_val, include_min=...,
include_max=...)` (layer 2) directly with `is_integer` instead.

---

## 3. Divisibility Parameters Are Independent

`divisible_by` and `has_remainder` can both be given at once — they are
not mutually exclusive the way `length` vs. `min_length`/`max_length` is,
so no conflict guard applies.
"""