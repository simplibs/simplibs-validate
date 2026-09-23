from .assert_type_contract import assert_type_contract
from .assert_type_validate_call_integration import assert_type_validate_call_integration
from .assert_validate_wrapper import assert_validate_wrapper


__all__ = [
    "assert_type_contract",
    "assert_type_validate_call_integration",
    "assert_validate_wrapper",
]


_DESIGN_NOTES = """
# Validate Testing Sub-Package

## Purpose
Public testing sub-package exporting assertion helpers and contract
orchestrators used to verify validated types, `@validate_call` integration,
and top-level validation wrapper functions.

## Exported Components Registry

| Component                               | Type     | Description                                                                  |
| :-------------------------------------- | :------- | :--------------------------------------------------------------------------- |
| `assert_type_contract`                  | Function | Master contract test orchestrator validating `validated_type()` type aliases. |
| `assert_type_validate_call_integration` | Function | Asserts that a validated type functions correctly inside `@validate_call`.   |
| `assert_validate_wrapper`               | Function | Validates top-level functional wrapper functions (`validate_int`, etc.).     |
"""