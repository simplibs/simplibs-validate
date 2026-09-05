from .build_validation_error import build_validation_error
from .ParamError import ParamError
from .ValidateError import ValidateError
from .ValidationError import ValidationError

__all__ = [
    "ValidateError",
    "ValidationError",
    "ParamError",
    "build_validation_error",
]


_DESIGN_NOTES = """
# Validation Exceptions Sub-Package

## Purpose
Defines the exception hierarchy for the entire `simplibs-validate` library:
the root exception type (`ValidateError`), specialized subtypes for data failures
(`ValidationError`) and configuration errors (`ParamError`), and the exception builder
factory.

## Internal Components Registry

| Component                 | Type     | Description                                                                 |
| :------------------------ | :------- | :-------------------------------------------------------------------------- |
| `ValidateError`           | Class    | Abstract root exception for all errors raised by the library.               |
| `ValidationError`        | Class    | Subclass of `ValidateError` raised when runtime input data fails validation. |
| `ParamError`               | Class    | Subclass of `ValidateError` raised for invalid rule/decorator setup.        |
| `build_validation_error`   | Function | Builds an exception instance for user-supplied callables/lambdas.           |
"""