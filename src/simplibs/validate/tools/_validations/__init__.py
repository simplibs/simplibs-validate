from .raise_override_rules_invalid_error import raise_override_rules_invalid_error
from .raise_validated_type_missing_rule_error import raise_validated_type_missing_rule_error
from .raise_validated_type_rule_invalid_error import raise_validated_type_rule_invalid_error


_DESIGN_NOTES = """
# Tools Internal Validations Sub-Package

## Purpose
Structured error-raising helpers used internally by `tools` functions
(`override_rules`, `validated_type`) to report misuse (missing rules,
invalid rule arguments) with a precise error message rather than a generic exception.

## Internal Components Registry

| Component                                 | Type     | Description                                                                  |
| :---------------------------------------- | :------- | :--------------------------------------------------------------------------- |
| `raise_override_rules_invalid_error`      | Function | Raised when `override_rules` receives an invalid rule parameter.             |
| `raise_validated_type_missing_rule_error` | Function | Raised when `validated_type` is called with zero rules.                      |
| `raise_validated_type_rule_invalid_error`  | Function | Raised when a given rule is neither a `Rule` nor callable in `validated_type`.|
"""