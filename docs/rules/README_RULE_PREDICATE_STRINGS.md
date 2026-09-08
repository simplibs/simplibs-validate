# 📦 `rules/predicates/strings` — String Content Rules

The `strings` package holds every rule that checks the *content* of a string —
substring/prefix/suffix membership, blankness, regex matching, and the reverse
"substring of" relationship — layered on top of a base `isinstance(value, str)` check
every rule in this package performs itself.

```python
from ..base_class import Rule

class Regex(Rule):
    ...
```

## A note on the shared `isinstance(value, str)` guard

Every rule in this package checks `isinstance(value, str)` as the first half of its
`is_valid` condition, using Python's short-circuit `and` so the string-specific method
(`.endswith()`, `.strip()`, `in`, ...) is never called on a non-string value. This
keeps each rule's `is_valid` a clean boolean expression rather than a `try/except
AttributeError` — a non-string input simply fails the first condition and never
reaches the second.

---

## 🧭 Table of Contents

* [`IsString`](#isstring)
* [`Contains`](#contains)
* [`IsSubstringOf`](#issubstringof)
* [`StartsWith`](#startswith)
* [`EndsWith`](#endswith)
* [`Regex`](#regex)
* [`IsBlank`](#isblank)
* [`NotBlank`](#notblank)

[⬅️ Back to main README](../../README.md#predicatesstrings--string-content)

---

### `IsString`

Value must be a string.

**Parameters:**
* *(none — takes only `self`)*

**Example usage:**
```python
validate(value, IsString())
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return isinstance(value, str)
```

[▲ Back to top](#-table-of-contents)

---

### `Contains`

String value must contain a given substring anywhere within it.

**Parameters:**
* `substring` (*str*): The substring that must be present.

**Example usage:**
```python
validate(value, Contains("@"))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, str)
        and self.substring in value
    )
```

[▲ Back to top](#-table-of-contents)

---

### `IsSubstringOf`

The **inverse** relationship of `Contains`: the value itself must appear *within* a
given target string, rather than containing something.

**Parameters:**
* `target_string` (*str*): The string the value must be found inside of.

**Example usage:**
```python
validate(value, IsSubstringOf("ADMIN_ROLE_FULL_ACCESS"))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, str)
        and value in self.target_string
    )
```

[▲ Back to top](#-table-of-contents)

---

### `StartsWith`

String value must start with a given prefix.

**Parameters:**
* `prefix` (*str*): The required prefix.

**Example usage:**
```python
validate(value, StartsWith("https://"))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, str)
        and value.startswith(self.prefix)
    )
```

[▲ Back to top](#-table-of-contents)

---

### `EndsWith`

String value must end with a given suffix.

**Parameters:**
* `suffix` (*str*): The required suffix.

**Example usage:**
```python
validate(value, EndsWith(".py"))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, str)
        and value.endswith(self.suffix)
    )
```

[▲ Back to top](#-table-of-contents)

---

### `Regex`

String value must match a given regular expression pattern — searched anywhere in the
string (via `re.search`), not required to match from the start or the whole string.
The pattern is compiled once at construction, not on every validation, and an invalid
pattern is rejected immediately rather than failing on first use.

**Parameters:**
* `pattern` (*str*): The regular expression pattern to search for.

**Example usage:**
```python
validate(value, Regex(r"^[a-z]+$"))
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, str)
        and self.compiled.search(value) is not None
    )
```

[▲ Back to top](#-table-of-contents)

---

### `IsBlank`

String value must be empty or contain only whitespace.

**Parameters:**
* *(none — takes only `self`)*

**Example usage:**
```python
validate(value, IsBlank())
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, str)
        and value.strip() == ""
    )
```

[▲ Back to top](#-table-of-contents)

---

### `NotBlank`

String value must contain at least one non-whitespace character — the direct inverse
of `IsBlank`, implemented independently for a more specific diagnostic message.

**Parameters:**
* *(none — takes only `self`)*

**Example usage:**
```python
validate(value, NotBlank())
```

**Under the hood** *(`is_valid`)*:
```python
def is_valid(self, value: Any) -> bool:
    return (
        isinstance(value, str)
        and value.strip() != ""
    )
```

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../README.md#predicatesstrings--string-content)