from .log_this import log_this
from .override_rules import override_rules
from .validate_call import validate_call
from .validate_dataclass import validate_dataclass
from .validated_type import validated_type

__all__ = [
    "log_this",
    "override_rules",
    "validate_call",
    "validate_dataclass",
    "validated_type",
]


_DESIGN_NOTES = """
# Validate Tools Sub-Package

## Purpose
Public tools package exporting core decorators for function validation,
dataclass field enforcement, custom parameter overrides, reusable annotated types,
and runtime execution logging.

## Exported Components Registry

| Component            | Type      | Description                                                                 |
| :------------------- | :-------- | :-------------------------------------------------------------------------- |
| `log_this`           | Decorator | Emits structured entry/exit/timing/exception logs via the module logger.    |
| `override_rules`     | Helper    | Attaches custom validation rule overrides directly to function parameters.  |
| `validate_call`      | Decorator | Validates function arguments and return values against typing rules.        |
| `validate_dataclass` | Decorator | Validates dataclass field values on instance construction.                 |
| `validated_type`     | Helper    | Builds reusable Annotated constructs combined with validation rules.        |
"""