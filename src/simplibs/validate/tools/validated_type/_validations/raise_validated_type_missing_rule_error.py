from typing import NoReturn
from ....exceptions import ParamError


def raise_validated_type_missing_rule_error(type_: object) -> NoReturn:
    """Raise a ParamError when validated_type() is called with zero rules.

    Args:
        type_: The target type — included for diagnostic context.

    Raises:
        ParamError: Always.
    """
    type_name = getattr(type_, "__name__", repr(type_))

    raise ParamError(
        error_name="VALIDATED_TYPE_MISSING_RULE_ERROR",
        label="rules",
        expected="at least one Rule instance or callable predicate",
        value=type_,
        problem=(
            f"validated_type({type_!r}) was called with zero validation rules.",
            "At least one rule or callable predicate is required.",
        ),
        how_to_fix=(
            f"Pass at least one rule, e.g. validated_type({type_name}, greater_than(0)).",
            f"If no constraint is needed, use '{type_name}' directly as the annotation.",
        ),
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_validated_type_missing_rule_error — validated_type() Diagnostic Helper

## Purpose
Guards validated_type()'s structural precondition: at least one rule must be given.

---

## 1. Execution Rationale

* **Tuple-Formatted Multi-Line Diagnostic Messages:**
  Uses structured `tuple` sequences for `problem` and `how_to_fix` fields to format
  clear, multi-line error cards with concrete code examples instead of monolithic strings.
"""