# 📄 `validate_number` — General Number Validation

Validates that a value is any kind of number — `int`, `float`, `Decimal`, or
`complex` (booleans excluded) — for callers who want "any number" rather than
committing to a specific numeric type. Built on top of `number_rule(...)`. See
[`validate_int`](README_VALIDATE_INT.md) / [`validate_float`](README_VALIDATE_FLOAT.md)
for the type-specific counterparts, which share almost the same parameter surface.

```python
validate_number(Decimal("3.5"), greater_than=0)
```

## Parameters

| Parameter          | Type                     | Default | Description                                                        |
|--------------------|---------------------------|---------|------------------------------------------------------------------------|
| `value`            | `Any`                     | —       | The value being validated.                                          |
| `greater_than`     | `Any \| None`            | `None`  | The value must be strictly greater than this threshold.             |
| `greater_or_equal` | `Any \| None`            | `None`  | The value must be greater than or equal to this threshold.          |
| `less_than`        | `Any \| None`            | `None`  | The value must be strictly less than this threshold.                |
| `less_or_equal`    | `Any \| None`            | `None`  | The value must be less than or equal to this threshold.             |
| `in_range`         | `tuple[Any, Any] \| None`| `None`  | Inclusive `(min_val, max_val)` range.                                |
| `positive`         | `bool`                    | `False` | If `True`, the value must be strictly greater than 0.                |
| `negative`         | `bool`                    | `False` | If `True`, the value must be strictly less than 0.                   |
| `equals`           | `Any \| None`            | `None`  | The value must equal this exact number.                              |
| `not_equals`       | `Any \| None`            | `None`  | The value must **not** equal this exact number.                      |
| `is_in`            | `Container[Any] \| None`| `None`  | The value must be one of the given options.                          |
| `not_in`           | `Container[Any] \| None`| `None`  | The value must **not** be one of the given options.                  |
| `value_name`       | `str \| None`            | `None`  | Name reported in diagnostics on failure.                              |
| `context`          | `str \| None`            | `None`  | Extra free-text context reported on failure.                          |
| `return_bool`      | `bool`                    | `False` | If `True`, returns `False` on failure instead of raising.             |
| `return_value`     | `bool`                    | `False` | If `True` and validation passes, returns `value` instead of `True`.   |

## Example usage

```python
validate_number(5, greater_than=0)
validate_number(2.5j)   # complex — passes IsNumber, no comparisons applied
```

## What it's built on: `number_rule`

```python
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
    parts: list[Rule] = [_is_number]

    if positive:
        parts.append(_greater_than(0))
    if negative:
        parts.append(_less_than(0))
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
    if equals is not None:
        parts.append(_equals(equals))
    if not_equals is not None:
        parts.append(_not_equals(not_equals))
    if is_in is not None:
        parts.append(_is_in(is_in))
    if not_in is not None:
        parts.append(_not_in(not_in))

    return AllOf(*parts) if len(parts) > 1 else parts[0]
```

Deliberately **no** `finite`, `divisible_by`, `has_remainder`, or `close_to_*`
parameters — `IsNan`/`IsInfinity`/`DivisibleBy`/`HasRemainder` are themselves
`float`/`int`-only checks and don't apply meaningfully to `Decimal`/`complex`, which
this function also accepts. Rather than silently skip those checks for non-matching
types, they're simply not exposed here — use `validate_int`/`validate_float` directly
when those specific constraints are needed. Comparisons against a `complex` value fail
cleanly with a "cannot compare" diagnostic (via the underlying comparison rules' own
`TypeError` handling) rather than crashing, since `complex` isn't orderable in Python.

---

[⬅️ Back to main README](../../README.md#2-specialized-validators)