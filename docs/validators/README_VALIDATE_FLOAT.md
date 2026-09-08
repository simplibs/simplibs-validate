# 📄 `validate_float` — Float Validation

Validates that a value is a `float`, with NaN/Infinity excluded by default, against a
set of numeric constraints. Built on top of `float_rule(...)`.

```python
validate_float(3.14, greater_than=0.0)
```

## Parameters

| Parameter          | Type                    | Default | Description                                                        |
|--------------------|--------------------------|---------|------------------------------------------------------------------------|
| `value`            | `Any`                    | —       | The value being validated.                                          |
| `greater_than`     | `float \| None`         | `None`  | The value must be strictly greater than this threshold.             |
| `greater_or_equal` | `float \| None`         | `None`  | The value must be greater than or equal to this threshold.          |
| `less_than`        | `float \| None`         | `None`  | The value must be strictly less than this threshold.                |
| `less_or_equal`    | `float \| None`         | `None`  | The value must be less than or equal to this threshold.             |
| `in_range`         | `tuple[float, float] \| None` | `None`  | Inclusive `(min_val, max_val)` range.                          |
| `positive`         | `bool`                   | `False` | If `True`, the value must be strictly greater than 0.               |
| `negative`         | `bool`                   | `False` | If `True`, the value must be strictly less than 0.                  |
| `close_to_target`  | `float \| None`         | `None`  | If given, the value must be approximately equal to this target.     |
| `close_to_rel_tol` | `float`                  | `1e-9`  | Relative tolerance for `close_to_target`.                            |
| `close_to_abs_tol` | `float`                  | `0.0`   | Absolute tolerance for `close_to_target`.                             |
| `finite`           | `bool`                   | `True`  | If `True`, excludes NaN and ±Infinity.                                |
| `equals`           | `float \| None`         | `None`  | The value must equal this exact float.                               |
| `not_equals`       | `float \| None`         | `None`  | The value must **not** equal this exact float.                       |
| `is_in`            | `Container[Any] \| None`| `None`  | The value must be one of the given options.                          |
| `not_in`           | `Container[Any] \| None`| `None`  | The value must **not** be one of the given options.                  |
| `value_name`       | `str \| None`           | `None`  | Name reported in diagnostics on failure.                              |
| `context`          | `str \| None`           | `None`  | Extra free-text context reported on failure.                          |
| `return_bool`      | `bool`                   | `False` | If `True`, returns `False` on failure instead of raising.             |
| `return_value`     | `bool`                   | `False` | If `True` and validation passes, returns `value` instead of `True`.   |

## Example usage

```python
validate_float(3.14, greater_than=0.0)
validate_float(float("nan"), finite=False)   # explicitly allow NaN
validate_float(3.14159, close_to_target=math.pi, close_to_rel_tol=1e-4)
```

## What it's built on: `float_rule`

```python
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
    parts: list[Rule] = [_is_float]

    if finite:
        parts.append(NoneOf(_is_nan, _is_infinity))
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
    if close_to_target is not None:
        parts.append(_close_to(close_to_target, rel_tol=close_to_rel_tol, abs_tol=close_to_abs_tol))
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

`finite` is the one constraint in this whole family that defaults to **on** rather
than "unconstrained" — a plain `isinstance(value, float)` check alone would happily
accept `float('nan')`/`float('inf')`, which is almost never the intent behind "give me
a float." Setting `finite=False` is a deliberate, visible opt-out. `close_to_target`'s
tolerance parameters are exposed as three separate keyword arguments rather than a
packed tuple (unlike `in_range`), since `CloseTo` itself takes `rel_tol`/`abs_tol` as
independently-defaulted keyword arguments — packing them would force specifying both
even when overriding only one.

---

[⬅️ Back to main README](../../README.md#2-specialized-validators)