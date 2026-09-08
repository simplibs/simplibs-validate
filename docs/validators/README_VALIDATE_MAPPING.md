# 📄 `validate_mapping` — Dict Validation

Validates that a value is a `dict` against key-membership and length constraints.
Built on top of `mapping_rule(...)` — the key-membership counterpart to
`validate_container`, layered on `IsInstance(dict)` rather than the broader
`IsContainer`.

```python
validate_mapping({"id": 1, "name": "x"}, has_keys=("id", "name"))
```

## Parameters

| Parameter    | Type                       | Default | Description                                                                 |
|--------------|-----------------------------|---------|--------------------------------------------------------------------------------|
| `value`      | `Any`                       | —       | The value being validated.                                                   |
| `min_length` | `int \| None`              | `None`  | Minimum allowed number of entries. Ignored if `length` is also given.        |
| `max_length` | `int \| None`              | `None`  | Maximum allowed number of entries. Ignored if `length` is also given.        |
| `length`     | `int \| None`              | `None`  | Exact required number of entries. Conflicts with `min_length`/`max_length`.  |
| `has_key`    | `Any \| UnsetType`         | `UNSET` | If given, the value must contain this single key.                            |
| `has_keys`   | `tuple[Any, ...] \| None`  | `None`  | If given, the value must contain all of these keys.                          |
| `value_name` | `str \| None`              | `None`  | Name reported in diagnostics on failure.                                     |
| `context`    | `str \| None`              | `None`  | Extra free-text context reported on failure.                                 |
| `return_bool`| `bool`                     | `False` | If `True`, returns `False` on failure instead of raising.                    |
| `return_value`| `bool`                    | `False` | If `True` and validation passes, returns `value` instead of `True`.          |

## Example usage

```python
validate_mapping({"id": 1}, has_key="id")
validate_mapping({"id": 1, "name": "x", "email": "y"}, has_keys=("id", "name"))
validate_mapping({}, min_length=1)
```

## What it's built on: `mapping_rule`

```python
def mapping_rule(
    *,
    min_length: int | None = None,
    max_length: int | None = None,
    length: int | None = None,
    has_key: Any | UnsetType = UNSET,
    has_keys: tuple[Any, ...] | None = None,
) -> Rule:
    parts: list[Rule] = [_is_instance(dict)]

    if length is not None or min_length is not None or max_length is not None:
        parts.append(_has_length(length, min_length=min_length, max_length=max_length))
    if has_key is not UNSET:
        parts.append(_has_key(has_key))
    if has_keys is not None:
        parts.append(_has_keys(*has_keys))

    return AllOf(*parts) if len(parts) > 1 else parts[0]
```

`has_key` is the one parameter in this whole family of `*_rule` functions that uses
the `UNSET` sentinel instead of plain `None` — because `None` is itself a perfectly
legitimate dict key, `has_key=None` ("must contain the key `None`") needs to stay
distinguishable from "no key constraint given at all." `has_keys` doesn't need this:
the *tuple itself* is never a meaningful key, even though individual keys inside it may
be `None`.

---

[⬅️ Back to main README](../../README.md#2-specialized-validators)