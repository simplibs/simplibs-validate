from .log_this import log_this
from .validate_call import validate_call
from .validate_dataclass import validate_dataclass

__all__ = [
    "log_this",
    "validate_call",
    "validate_dataclass",
]


_DESIGN_NOTES = """
# Validate Tools Sub-Package

## Purpose
Public tools package exporting core decorators for function validation,
dataclass field enforcement, and runtime execution logging.

## Exported Components Registry

| Component            | Type      | Description                                                                 |
| :------------------- | :-------- | :-------------------------------------------------------------------------- |
| `log_this`           | Decorator | Emits structured entry/exit/timing/exception logs via the module logger.    |
| `validate_call`      | Decorator | Validates function arguments and return values against typing rules.        |
| `validate_dataclass` | Decorator | Validates dataclass field values on instance construction.                 |
"""