from .raise_invalid_max_items import raise_invalid_max_items


_DESIGN_NOTES = """
# Log This Diagnostic Helpers Sub-Package

## Purpose
Structured ParamError raisers for `@log_this` configuration mistakes, mirroring the
`_validations` package of `validate_call`.

## Internal Components Registry

| Component                | Type     | Description                                                           |
| :----------------------- | :------- | :-------------------------------------------------------------------- |
| `raise_invalid_max_items` | Function | Raises a ParamError for a `max_items` that is not None or a positive int. |
"""
