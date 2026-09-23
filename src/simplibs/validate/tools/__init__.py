from .override_rules import override_rules
from .validated_type import validated_type

__all__ = [
    "override_rules",
    "validated_type",
]


_DESIGN_NOTES = """
# Validate Tools Sub-Package

## Purpose
Provides operational helper utilities that work alongside the validation system,
enabling parameter overrides, unconditional exception triggers, and reusable
type-annotated validation aliases.

## Registry

| Component        | Type     | Description                                                                          |
| :--------------- | :------- | :----------------------------------------------------------------------------------- |
| `override_rules` | Helper   | Attaches custom validation rule overrides directly to function parameters.           |
| `validated_type` | Helper   | Factory for creating reusable Annotated type aliases bound to specific rule sets.    |
"""