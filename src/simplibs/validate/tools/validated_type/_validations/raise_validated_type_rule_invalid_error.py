from typing import Any, NoReturn
from ....exceptions import ParamError


def raise_validated_type_rule_invalid_error(rule: Any, index: int) -> NoReturn:
    """Raise a ParamError when one of validated_type()'s rules is neither
    a Rule instance nor callable.

    Args:
        rule: The invalid rule value.
        index: Position of the rule (0-based index).

    Raises:
        ParamError: Always.
    """
    raise ParamError(
        error_name="VALIDATED_TYPE_RULE_INVALID_ERROR",
        label="rules",
        expected="a Rule instance or a callable predicate",
        value=rule,
        problem=(
            f"The rule at position {index} in validated_type() is invalid.",
            f"Received {rule!r}, which is neither a Rule instance nor a callable.",
        ),
        how_to_fix=(
            "Provide a valid Rule instance or callable predicate at every position.",
            "Example with Rule: validated_type(int, greater_than(0))",
            "Example with callable: validated_type(int, lambda v: v > 0)",
        ),
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_validated_type_rule_invalid_error — validated_type() Diagnostic Helper

## Purpose
Guards validated_type()'s positional rule arguments for validity.

---

## 1. Execution Rationale

* **Tuple-Formatted Multi-Line Diagnostic Messages:**
  Uses structured `tuple` sequences for `problem` and `how_to_fix` fields to format
  clear, multi-line error cards with concrete code examples instead of monolithic strings.
"""