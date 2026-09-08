# 📄 `validate_str` — String Validation

Validates that a value is a `str` against a broad set of content constraints. Built
on top of `string_rule(...)`.

```python
validate_str("user@example.com", contains="@", min_length=5)
```

## Parameters

| Parameter          | Type                     | Default | Description                                                                 |
|--------------------|---------------------------|---------|----------------------------------------------------------------------------------|
| `value`            | `Any`                     | —       | The value being validated.                                                    |
| `min_length`       | `int \| None`            | `None`  | Minimum allowed length. Ignored if `length` is also given.                    |
| `max_length`       | `int \| None`            | `None`  | Maximum allowed length. Ignored if `length` is also given.                    |
| `length`           | `int \| None`            | `None`  | Exact required length. Conflicts with `min_length`/`max_length`.              |
| `starts_with`      | `str \| None`            | `None`  | Required prefix.                                                              |
| `ends_with`        | `str \| None`            | `None`  | Required suffix.                                                              |
| `contains`         | `str \| None`            | `None`  | Required substring.                                                           |
| `is_substring_of`  | `str \| None`            | `None`  | Target string in which the evaluated string must be contained.                |
| `regex_search`     | `str \| None`            | `None`  | Required regex pattern, matched anywhere via `re.search` (not an anchored full match). |
| `is_blank`         | `bool \| None`           | `None`  | If `None`, unconstrained. If `True`, must be blank. If `False`, must **not** be blank. |
| `equals`           | `str \| None`            | `None`  | The value must equal this exact string.                                       |
| `not_equals`       | `str \| None`            | `None`  | The value must **not** equal this exact string.                               |
| `is_in`            | `Container[Any] \| None`| `None`  | The value must be one of the given options.                                   |
| `not_in`           | `Container[Any] \| None`| `None`  | The value must **not** be one of the given options.                           |
| `value_name`       | `str \| None`            | `None`  | Name reported in diagnostics on failure.                                       |
| `context`          | `str \| None`            | `None`  | Extra free-text context reported on failure.                                   |
| `return_bool`      | `bool`                    | `False` | If `True`, returns `False` on failure instead of raising.                      |
| `return_value`     | `bool`                    | `False` | If `True` and validation passes, returns `value` instead of `True`.            |

## Example usage

```python
validate_str("hello world", starts_with="hello")
validate_str("draft", is_in=("draft", "published"))
validate_str("", is_blank=True)
```

## What it's built on: `string_rule`

```python
def string_rule(
    *,
    min_length: int | None = None,
    max_length: int | None = None,
    length: int | None = None,
    starts_with: str | None = None,
    ends_with: str | None = None,
    contains: str | None = None,
    is_substring_of: str | None = None,
    regex_search: str | None = None,
    is_blank: bool | None = None,
    equals: str | None = None,
    not_equals: str | None = None,
    is_in: Container[Any] | None = None,
    not_in: Container[Any] | None = None,
) -> Rule:
    parts = [_is_string]

    if length is not None or min_length is not None or max_length is not None:
        parts.append(_has_length(length, min_length=min_length, max_length=max_length))
    if starts_with is not None:
        parts.append(_starts_with(starts_with))
    if ends_with is not None:
        parts.append(_ends_with(ends_with))
    if contains is not None:
        parts.append(_contains(contains))
    if is_substring_of is not None:
        parts.append(_is_substring_of(is_substring_of))
    if regex_search is not None:
        parts.append(_regex(regex_search))
    if is_blank is not None:
        parts.append(_is_blank if is_blank else _not_blank)
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

`regex_search` is named for exactly what it does (`re.search` — anywhere in the
string, not an anchored full match), rather than the more generic `pattern`.
`is_blank` is tri-state, not a plain bool: `None` means "don't care," `True`/`False`
add `IsBlank`/`NotBlank` respectively — this lets the rule express both "must be
blank" and "must not be blank" without a separate parameter for each.

---

[⬅️ Back to main README](../../README.md#2-specialized-validators)