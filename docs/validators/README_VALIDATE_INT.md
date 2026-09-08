# 📄 `validate_int` — Integer Validation

Validates that a value is an `int` (excluding `bool`) against a set of numeric and
divisibility constraints. Built on top of `integer_rule(...)`.

```python
validate_int(4, divisible_by=2)
```

## Parameters

| Parameter          | Type                        | Default | Description                                                              |
|--------------------|------------------------------|---------|------------------------------------------------------------------------------|
| `value`            | `Any`                        | —       | The value being validated.                                                |
| `greater_than`     | `int \| None`               | `None`  | The value must be strictly greater than this threshold.                   |
| `greater_or_equal` | `int \| None`               | `None`  | The value must be greater than or equal to this threshold.                |
| `less_than`        | `int \| None`               | `None`  | The value must be strictly less than this threshold.                      |
| `less_or_equal`    | `int \| None`               | `None`  | The value must be less than or equal to this threshold.                   |
| `in_range`         | `tuple[int, int] \| None`   | `None`  | Inclusive `(min_val, max_val)` range.                                       |
| `positive`         | `bool`                       | `False` | If `True`, the value must be strictly greater than 0 (shortcut for `greater_than=0`). |
| `negative`         | `bool`                       | `False` | If `True`, the value must be strictly less than 0 (shortcut for `less_than=0`). |
| `divisible_by`     | `int \| None`               | `None`  | The value must be evenly divisible by this divisor.                        |
| `has_remainder`    | `tuple[int, int] \| None`   | `None`  | `(divisor, remainder)` — exact remainder required when divided by `divisor`. |
| `equals`           | `int \| None`               | `None`  | The value must equal this exact integer.                                   |
| `not_equals`       | `int \| None`               | `None`  | The value must **not** equal this exact integer.                           |
| `is_in`            | `Container[Any] \| None`    | `None`  | The value must be one of the given options.                                |
| `not_in`           | `Container[Any] \| None`    | `None`  | The value must **not** be one of the given options.                        |
| `value_name`       | `str \| None`               | `None`  | Name reported in diagnostics on failure.                                    |
| `context`          | `str \| None`               | `None`  | Extra free-text context reported on failure.                                |
| `return_bool`      | `bool`                       | `False` | If `True`, returns `False` on failure instead of raising.                   |
| `return_value`     | `bool`                       | `False` | If `True` and validation passes, returns `value` instead of `True`.         |

## Example usage

```python
validate_int(42, positive=True)
validate_int(7, divisible_by=7)
validate_int(10, has_remainder=(3, 1))
```

## What it's built on: `integer_rule`

```python
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
    parts: list[Rule] = [_is_integer]

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
    if divisible_by is not None:
        parts.append(_divisible_by(divisible_by))
    if has_remainder is not None:
        divisor, remainder_val = has_remainder
        parts.append(_has_remainder(divisor, remainder_val))
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

`positive`/`negative` are unambiguous sugar for `greater_than=0`/`less_than=0` — not
new rule classes — because "positive" is itself ambiguous (does it include zero?) in
ordinary usage; baking one interpretation into a permanent class name would decide
that silently for every caller. A caller wanting the zero-inclusive reading uses
`greater_or_equal=0` directly. `divisible_by` and `has_remainder` can both be given at
once; unlike `length` vs. `min_length`/`max_length`, there's no meaningful conflict
between them.

---

[⬅️ Back to main README](../../README.md#2-specialized-validators)