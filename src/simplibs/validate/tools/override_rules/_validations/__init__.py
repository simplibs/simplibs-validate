from .raise_override_rules_invalid_error import raise_override_rules_invalid_error

_DESIGN_NOTES = """
# Override Rules Internal Validations Sub-Package

## Purpose
Internal error-raising functions for `override_rules` argument validation.

## Internal Components Registry

| Component                            | Type     | Description                                                                    |
| :----------------------------------- | :------- | :----------------------------------------------------------------------------- |
| `raise_override_rules_invalid_error` | Function | Raises ParamError when a rule override is neither a Rule instance nor callable. |
"""