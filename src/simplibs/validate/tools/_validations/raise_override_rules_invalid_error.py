from typing import Any, NoReturn
from simplibs.exception import ParamError


def raise_override_rules_invalid_error(
    name: str, rule: Any
) -> NoReturn:
    """Raise a ParamError when one of override_rules()'s values is neither
    a Rule instance nor callable.

    Args:
        name: The parameter name this rule was given for.
        rule: The invalid value.

    Raises:
        ParamError: Always.
    """
    raise ParamError(
        error_name="OVERRIDE_RULES_INVALID_ERROR",
        label=name,
        expected="a Rule instance or a callable predicate",
        value=rule,
        problem=(
            f"The value supplied for parameter '{name}' is invalid.",
            f"Received {rule!r}, which is neither a Rule instance nor a callable.",
        ),
        how_to_fix=(
            f"Provide a valid Rule instance or callable predicate for '{name}'.",
            "Example with Rule: override_rules(age=greater_than(0))",
            "Example with callable: override_rules(age=lambda v: v > 0)",
        ),
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_override_rules_invalid_error — override_rules() Diagnostic Helper

## Purpose
Guards override_rules()'s one precondition — every value must be
something UserRule/AllOf can actually use. Python's **kwargs syntax
already guarantees the *keys* are valid parameter names, so nothing
structural needs checking here; only the *value* at each key can still be wrong,
and this catches that immediately, naming which parameter's rule was invalid.

---

## 1. Execution Rationale

* **Tuple-Formatted Multi-Line Diagnostic Messages:**
  Uses structured `tuple` sequences for `problem` and `how_to_fix` fields to format
  clear, multi-line error cards with concrete code examples instead of monolithic strings.
"""