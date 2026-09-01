from .build_validation_error import build_validation_error
from .ParamError import ParamError
from .ValidateError import ValidateError


_DESIGN_NOTES = """
# Validation Exceptions Sub-Package

## Purpose
Defines the exception hierarchy for the entire `simplibs-validate` library:
the single root exception type, a specialized subtype for developer
configuration errors, and the factory used to build exceptions for
user-supplied callables/lambdas.

## Internal Components Registry

| Component                 | Type      | Description                                                                 |
| :------------------------ | :-------- | :---------------------------------------------------------------------------|
| `ValidateError`            | Class     | Root exception for all validation errors raised by the library.             |
| `ParamError`                | Class     | Subclass of `ValidateError` for invalid rule-constructor parameters.        |
| `build_validation_error`    | Function  | Builds a `ValidateError` for user-supplied callables/lambdas (not `Rule`).  |
"""