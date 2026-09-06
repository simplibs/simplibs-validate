from .raise_validated_type_missing_rule_error import raise_validated_type_missing_rule_error
from .raise_validated_type_rule_invalid_error import raise_validated_type_rule_invalid_error


_DESIGN_NOTES = """
# Validated Type Internal Validations Sub-Package

## Purpose
Internal error-raising functions for `validated_type` argument validation.

## Internal Components Registry

| Component                                 | Type     | Description                                                                 |
| :---------------------------------------- | :------- | :-------------------------------------------------------------------------- |
| `raise_validated_type_missing_rule_error` | Function | Raises ParamError when `validated_type` is called without any rules.        |
| `raise_validated_type_rule_invalid_error` | Function | Raises ParamError when a rule argument is neither a Rule nor a callable.  |
"""