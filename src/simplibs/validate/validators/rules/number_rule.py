from typing import Any, Container
from simplibs.rules import (
    Rule,
    AllOf,
    is_number as _is_number,
    greater_than as _greater_than,
    greater_or_equal as _greater_or_equal,
    less_than as _less_than,
    less_or_equal as _less_or_equal,
    in_range as _in_range,
    equals as _equals,
    not_equals as _not_equals,
    is_in as _is_in,
    not_in as _not_in,
)


def number_rule(
    *,
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
) -> Rule:
    """Compose a Rule validating any number (int, float, Decimal, complex —
    booleans excluded) against the given optional constraints.

    Args:
        greater_than: The value must be strictly greater than this threshold.
        greater_or_equal: The value must be greater than or equal to this threshold.
        less_than: The value must be strictly less than this threshold.
        less_or_equal: The value must be less than or equal to this threshold.
        in_range: (min_val, max_val) — inclusive range. For custom bound
            inclusivity, compose InRange directly instead.
        positive: If True, the value must be strictly greater than 0.
        negative: If True, the value must be strictly less than 0.
        equals: The value must equal this exact number.
        not_equals: The value must NOT equal this exact number.
        is_in: The value must be one of the given options.
        not_in: The value must NOT be one of the given options.

    Returns:
        A single Rule instance — `is_number` itself if no constraint is
        given, otherwise an AllOf combining the type check with every
        given constraint.
    """
    # 1. Base type check
    parts: list[Rule] = [_is_number]

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

    # 4. Identity / membership
    if equals is not None:
        parts.append(_equals(equals))
    if not_equals is not None:
        parts.append(_not_equals(not_equals))
    if is_in is not None:
        parts.append(_is_in(is_in))
    if not_in is not None:
        parts.append(_not_in(not_in))

    # 5. Collapse to a single Rule
    return (
        AllOf(*parts)
        if len(parts) > 1
        else parts[0]
    )


_DESIGN_NOTES = """
# number_rule — Composed General Number Validation Rule

## Purpose
Layer-3 composition over `IsNumber` (layer 1) / `is_number` (layer 2) —
the broad numeric umbrella (`int`, `float`, `Decimal`, `complex`;
booleans excluded), for callers who want "any number" rather than
committing to a specific numeric type. See `integer_rule.py` /
`float_rule.py` for the type-specific counterparts, which share almost
the same parameter surface, and `string_rule.py` for the shared pattern.

---

## 1. No `finite` Parameter (Unlike `float_rule`)

`IsNan`/`IsInfinity` are themselves `float`-only checks — they do not
apply to `Decimal` or `complex` inputs, which this rule also accepts.
Rather than silently skip the finite check for non-float numeric types
(inconsistent) or raise on non-float input (surprising for a rule meant
to accept any number), `number_rule` simply does not offer this
constraint. Callers who specifically want `float` and finiteness should
use `float_rule` instead.

---

## 2. No `divisible_by`/`has_remainder`/`close_to`

Omitted for the same reason: `DivisibleBy`/`HasRemainder` require `int`,
and `CloseTo` is meaningful primarily for `int`/`float`. Rather than let
them silently fail for `Decimal`/`complex` input, they are simply not
exposed here — use `integer_rule`/`float_rule` directly when needed.

---

## 3. Comparisons Against Non-Orderable Numbers (`complex`)

Comparison parameters pass straight through to the underlying rules,
which already handle incomparable types gracefully (catching `TypeError`
internally and reporting a clear diagnostic rather than crashing). No
special-casing was needed here to achieve that.
"""