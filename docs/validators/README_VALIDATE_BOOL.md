# 📄 `validate_bool` — Boolean Validation

Validates that a value is a boolean, optionally requiring an exact expected value.
Built on top of `boolean_rule(...)`, which composes the underlying `Rule` this
function immediately validates against via `Rule.validate(...)`.

```python
validate_bool(True, equals=True)
```

## Parameters

| Parameter      | Type            | Default | Description                                                    |
|----------------|-----------------|---------|------------------------------------------------------------------|
| `value`        | `Any`           | —       | The value being validated.                                      |
| `equals`       | `bool \| None`  | `None`  | If given, the value must equal this exact boolean.               |
| `value_name`   | `str \| None`   | `None`  | Name reported in diagnostics on failure.                         |
| `context`      | `str \| None`   | `None`  | Extra free-text context reported on failure.                     |
| `return_bool`  | `bool`          | `False` | If `True`, returns `False` on failure instead of raising.        |
| `return_value` | `bool`          | `False` | If `True` and validation passes, returns `value` instead of `True`. |

## Example usage

```python
validate_bool(True)
validate_bool(True, equals=True)
validate_bool(False, equals=True, return_bool=True)     # -> False, no exception
```

## What it's built on: `boolean_rule`

`boolean_rule(...)` composes the `Rule` instance `validate_bool` validates against —
`is_bool` alone if `equals` isn't given, otherwise combined with `Equals` via `AllOf`.
It's the deliberately minimal member of this family: booleans have essentially one
meaningful optional constraint beyond their type.

```python
def boolean_rule(*, equals: bool | None = None) -> Rule:
    parts: list[Rule] = [_is_bool]

    if equals is not None:
        parts.append(_equals(equals))

    return AllOf(*parts) if len(parts) > 1 else parts[0]
```

> 💡 For repeated validation against the same constraints (e.g. inside a loop), build
> the rule once with `boolean_rule(...)` and reuse it directly, rather than calling
> `validate_bool(...)` per value — `validate_bool` rebuilds the rule on every call.

---

[⬅️ Back to main README](../../README.md#2-specialized-validators)