# 📄 `validate_container` — Container Validation

Validates that a value is a container (any non-string collection — `list`, `tuple`,
`set`, `dict`, ...) against a set of optional structural constraints. Built on top of
`container_rule(...)`.

```python
validate_container([1, 2, 3], unique=True, min_length=1)
```

## Parameters

| Parameter      | Type                                | Default | Description                                                              |
|----------------|--------------------------------------|---------|----------------------------------------------------------------------------|
| `value`        | `Any`                                 | —       | The value being validated.                                                |
| `min_length`   | `int \| None`                        | `None`  | Minimum allowed number of items. Ignored if `length` is also given.       |
| `max_length`   | `int \| None`                        | `None`  | Maximum allowed number of items. Ignored if `length` is also given.       |
| `length`       | `int \| None`                        | `None`  | Exact required number of items. Conflicts with `min_length`/`max_length`. |
| `unique`       | `bool`                                | `False` | If `True`, every item must be unique.                                     |
| `has_item`     | `Any \| None`                        | `None`  | If given, the value must contain this single item.                        |
| `subset_of`    | `Collection[Any] \| None`            | `None`  | If given, every item in the value must appear in this reference collection. |
| `superset_of`  | `Collection[Any] \| None`            | `None`  | If given, every item in this reference collection must appear in the value. |
| `for_each`     | `Rule \| Callable[[Any], bool] \| None` | `None`  | If given, every item in the value must satisfy this rule or callable.     |
| `value_name`   | `str \| None`                        | `None`  | Name reported in diagnostics on failure.                                  |
| `context`      | `str \| None`                        | `None`  | Extra free-text context reported on failure.                              |
| `return_bool`  | `bool`                                | `False` | If `True`, returns `False` on failure instead of raising.                 |
| `return_value` | `bool`                                | `False` | If `True` and validation passes, returns `value` instead of `True`.       |

## Example usage

```python
validate_container([1, 2, 3], unique=True)
validate_container(["admin", "editor"], has_item="admin")
validate_container([1, 2], for_each=is_integer)
```

## What it's built on: `container_rule`

```python
def container_rule(
    *,
    min_length: int | None = None,
    max_length: int | None = None,
    length: int | None = None,
    unique: bool = False,
    has_item: Any | None = None,
    subset_of: Collection[Any] | None = None,
    superset_of: Collection[Any] | None = None,
    for_each: Rule | Callable[[Any], bool] | None = None,
) -> Rule:
    parts: list[Rule] = [_is_container]

    if length is not None or min_length is not None or max_length is not None:
        parts.append(_has_length(length, min_length=min_length, max_length=max_length))
    if unique:
        parts.append(_all_unique)
    if has_item is not None:
        parts.append(_has_item(has_item))
    if subset_of is not None:
        parts.append(_is_subset_of(subset_of))
    if superset_of is not None:
        parts.append(_is_superset_of(superset_of))
    if for_each is not None:
        parts.append(ForEach(for_each))

    return AllOf(*parts) if len(parts) > 1 else parts[0]
```

`length` is passed straight through to `HasLength` without being pre-checked against
`min_length`/`max_length` here — `HasLength` itself already raises on that conflict,
so there is no reason to duplicate the guard at this layer. `for_each` is the one
parameter that reaches back into layer-1/2 rules directly: it accepts an entire `Rule`
or callable rather than a scalar value, since expressing "every item satisfies X" needs
a full per-item rule, not a fixed constraint this function could build on its own.

Mapping-specific checks (`has_key`, `has_keys`) are deliberately **not** included here
— see [`validate_mapping`](README_VALIDATE_MAPPING.md) instead, which layers on top of
`IsInstance(dict)` rather than the broader `IsContainer`.

---

[⬅️ Back to main README](../../README.md#2-specialized-validators)