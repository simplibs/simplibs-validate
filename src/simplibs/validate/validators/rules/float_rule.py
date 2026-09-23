from typing import Any, Container
from simplibs.rules import (
    Rule,
    AllOf,
    NoneOf,
    is_float as _is_float,
    greater_than as _greater_than,
    greater_or_equal as _greater_or_equal,
    less_than as _less_than,
    less_or_equal as _less_or_equal,
    in_range as _in_range,
    close_to as _close_to,
    is_nan as _is_nan,
    is_infinity as _is_infinity,
    equals as _equals,
    not_equals as _not_equals,
    is_in as _is_in,
    not_in as _not_in,
)


def float_rule(
    *,
    greater_than: float | None = None,
    greater_or_equal: float | None = None,
    less_than: float | None = None,
    less_or_equal: float | None = None,
    in_range: tuple[float, float] | None = None,
    positive: bool = False,
    negative: bool = False,
    close_to_target: float | None = None,
    close_to_rel_tol: float = 1e-9,
    close_to_abs_tol: float = 0.0,
    finite: bool = True,
    equals: float | None = None,
    not_equals: float | None = None,
    is_in: Container[Any] | None = None,
    not_in: Container[Any] | None = None,
) -> Rule:
    """Compose a Rule validating a float against the given optional constraints.

    Args:
        greater_than: The value must be strictly greater than this threshold.
        greater_or_equal: The value must be greater than or equal to this threshold.
        less_than: The value must be strictly less than this threshold.
        less_or_equal: The value must be less than or equal to this threshold.
        in_range: (min_val, max_val) — inclusive range. For custom bound
            inclusivity, compose InRange directly instead.
        positive: If True, the value must be strictly greater than 0.
        negative: If True, the value must be strictly less than 0.
        close_to_target: If given, the value must be approximately equal
            to this target (via CloseTo), using close_to_rel_tol/close_to_abs_tol.
        close_to_rel_tol: Relative tolerance for close_to_target. Ignored
            if close_to_target is not given.
        close_to_abs_tol: Absolute tolerance for close_to_target. Ignored
            if close_to_target is not given.
        finite: If True (default), excludes NaN and +/-Infinity — a plain
            `isinstance(value, float)` check alone would let both through.
            Set to False to allow NaN/Infinity through unconstrained.
        equals: The value must equal this exact float.
        not_equals: The value must NOT equal this exact float.
        is_in: The value must be one of the given options.
        not_in: The value must NOT be one of the given options.

    Returns:
        A single Rule instance — `is_float` itself if no constraint is
        given (finite=False case), otherwise an AllOf combining the type
        check with every given constraint.
    """
    # 1. Base type check
    parts: list[Rule] = [_is_float]

    # 2. Finiteness
    if finite:
        parts.append(NoneOf(_is_nan, _is_infinity))

    # 3. Sign shortcuts
    if positive:
        parts.append(_greater_than(0))
    if negative:
        parts.append(_less_than(0))

    # 4. Comparisons
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

    # 5. Approximate equality
    if close_to_target is not None:
        parts.append(_close_to(
            close_to_target,
            rel_tol=close_to_rel_tol,
            abs_tol=close_to_abs_tol,
        ))

    # 6. Identity / membership
    if equals is not None:
        parts.append(_equals(equals))
    if not_equals is not None:
        parts.append(_not_equals(not_equals))
    if is_in is not None:
        parts.append(_is_in(is_in))
    if not_in is not None:
        parts.append(_not_in(not_in))

    # 7. Collapse to a single Rule
    return (
        AllOf(*parts)
        if len(parts) > 1
        else parts[0]
    )


_DESIGN_NOTES = """
# float_rule — Composed Float Validation Rule

## Purpose
Layer-3 composition over `IsFloat` (layer 1) / `is_float` (layer 2). See
`string_rule.py`'s design notes for the shared pattern.

---

## 1. `finite: bool = True` — The One Constraint That Is On By Default

Every other optional constraint here defaults to `None` ("not requested,
don't add it"). `finite` is the sole exception: it defaults to `True` and
is active unless the caller explicitly opts out with `finite=False`.

**Why:** `isinstance(value, float)` alone happily accepts `float('nan')`
and `float('inf')` — both are, structurally, floats. For the overwhelming
majority of real-world "give me a float" validation, silently accepting
NaN or Infinity is almost always a latent bug waiting to surface
downstream. Requiring `finite=False` to be typed out explicitly makes "I
actually want to allow NaN/Infinity" a deliberate, visible choice rather
than the silent default.

This means `float_rule()` with zero other arguments does *not* hit the
zero-overhead single-rule fast path the way `boolean_rule()`/
`integer_rule()` do when called with no arguments — it always composes at
least `AllOf(IsFloat(), NoneOf(IsNan(), IsInfinity()))`.
`float_rule(finite=False)` is the only way to get back down to bare
`is_float`.

* **Built via `NoneOf`, Not Two Separate `Not(...)` Rules:** `NoneOf`
  reads as a single, clear constraint and produces one diagnostic card
  naming both forbidden conditions together, rather than two separately
  nested `Not` rules with separate error paths.

---

## 2. `close_to_*` Parameters Are Flattened, Not a Tuple

Unlike `in_range`/`has_remainder` (2-tuples), `CloseTo`'s tolerance
parameters are exposed as three separate keyword arguments rather than a
packed tuple. `CloseTo` itself takes `rel_tol`/`abs_tol` as keyword-only
parameters with meaningful defaults — packing them into a tuple would
force the caller to always specify both even when overriding only one.

Note `close_to_rel_tol`/`close_to_abs_tol` are plain floats with real
defaults (`1e-9`/`0.0`), not `None`-sentinel optional constraints — they
are tuning knobs for `close_to_target`, meaningless on their own, and are
simply ignored if `close_to_target` is not given.
"""