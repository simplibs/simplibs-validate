from typing import Any, Callable
# Inners
from .ValidateError import ValidateError


def build_validation_error(
    rule: Callable[[Any], bool],
    value: Any,
    value_name: str | None = None,
    context: str | None = None,
) -> Exception:
    """Build a structured `ValidateError` exception for a failed user function or lambda."""
    rule_name = getattr(rule, "__name__", str(rule))

    return ValidateError(
        error_name="VALIDATION_ERROR",
        label=value_name,
        expected=f"value satisfying callable condition '{rule_name}'",
        value=value,
        problem=f"Value failed validation check executed by callable '{rule_name}'.",
        context=context,
        how_to_fix=(
            f"Provide a value that evaluates to True when passed to '{rule_name}'.",
        ),
        exception=ValueError,
    )


_DESIGN_NOTES = """
# build_validation_error — Exception Factory for User-Defined Rules

## Purpose
This function exists solely to build a structured `ValidateError` exception
for cases where validation runs through a user-supplied ad-hoc rule (one that
does not inherit from the `Rule` class). This covers any callable object —
an anonymous function (`lambda`), a plain function, or an object with a
`__call__` method — that returns a `bool`.

---

## 1. Rationale

* **Built-in vs. User Rules:**
  Internal built-in rules (derived from `Rule`) have their own
  `build_exception()` methods, where they define precise, rule-specific
  `expected`, `problem`, and `how_to_fix` messages.
* **Fallback for Ad-Hoc Functions:**
  If the user passes a rule such as `lambda x: x > 0`, the system has no
  access to any class with a predefined error message. `build_validation_error`
  extracts the function/lambda name and generates a consistent diagnostic
  card on its behalf.
"""