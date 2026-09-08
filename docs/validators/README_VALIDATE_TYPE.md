# 📄 `validate_type` — Class/Type Object Validation

Validates that a value is itself a class object (not an instance), with optional
inheritance and identity constraints. Built on top of `type_rule(...)`.

```python
validate_type(bool, subclass_of=(int,))
```

## Parameters

| Parameter     | Type                       | Default | Description                                                              |
|---------------|-----------------------------|---------|--------------------------------------------------------------------------|
| `value`       | `Any`                       | —       | The value being validated.                                              |
| `subclass_of` | `tuple[type, ...] \| None` | `None`  | If given, the value must be a subclass of one or more of these base classes. |
| `equals`      | `type \| None`             | `None`  | The value must equal (be identical to) this exact class.                 |
| `not_equals`  | `type \| None`             | `None`  | The value must **not** equal this exact class.                           |
| `is_in`       | `Container[type] \| None` | `None`  | The value must be one of the given classes.                              |
| `not_in`      | `Container[type] \| None` | `None`  | The value must **not** be one of the given classes.                      |
| `value_name`  | `str \| None`              | `None`  | Name reported in diagnostics on failure.                                  |
| `context`     | `str \| None`              | `None`  | Extra free-text context reported on failure.                              |
| `return_bool` | `bool`                      | `False` | If `True`, returns `False` on failure instead of raising.                 |
| `return_value`| `bool`                      | `False` | If `True` and validation passes, returns `value` instead of `True`.       |

## Example usage

```python
validate_type(bool, subclass_of=(int,))
validate_type(MyClass, equals=MyClass)
validate_type(int, is_in=(int, float, str))
```

## What it's built on: `type_rule`

```python
def type_rule(
    *,
    subclass_of: tuple[type, ...] | None = None,
    equals: type | None = None,
    not_equals: type | None = None,
    is_in: Container[type] | None = None,
    not_in: Container[type] | None = None,
) -> Rule:
    parts: list[Rule] = [_is_type]

    if subclass_of is not None:
        parts.append(_is_subclass(*subclass_of))
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

`subclass_of` is always given as a tuple — even for one base class — because
`IsSubclass(*types)` itself is variadic, and this composed layer exposes it as one
keyword argument (`subclass_of=(BaseClass,)`) unpacked with `*subclass_of` when
building `IsSubclass`. This differs from `is_in`/`not_in`, which also take a container
but pass it through to `IsIn`/`NotIn` as a single argument, not unpacked — the
distinction follows each underlying rule's own constructor signature, not an
arbitrary choice made at this layer. The leading `IsType()` check is technically
redundant once `subclass_of` is given (`IsSubclass` already verifies its input is a
class internally), but is kept for a consistent base predicate and a clearer
first-failure diagnostic when the value isn't a class at all.

---

[⬅️ Back to main README](../../README.md#2-specialized-validators)