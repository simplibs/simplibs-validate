from .raise_no_rule_for_checked_param import raise_no_rule_for_checked_param
from .raise_no_rule_for_return import raise_no_rule_for_return


_DESIGN_NOTES = """
# Validate Call Internal Diagnostic Helpers Sub-Package

## Purpose
Internal diagnostic helpers used by `validate_call` compilation steps to raise
structured `ParamError` exceptions when validation requirements cannot be met
(e.g., missing annotations or override rules).

## Internal Components Registry

| Component                         | Type     | Description                                                                     |
| :-------------------------------- | :------- | :------------------------------------------------------------------------------ |
| `raise_no_rule_for_checked_param` | Function | Raises `ParamError` when a parameter listed in `check` lacks a rule source.     |
| `raise_no_rule_for_return`        | Function | Raises `ParamError` when `check_return=True` is set without a return annotation.|
"""