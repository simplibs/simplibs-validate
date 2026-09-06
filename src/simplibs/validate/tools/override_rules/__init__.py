from .override_rules import override_rules


_DESIGN_NOTES = """
# Override Rules Tool Sub-Package

## Purpose
Provides helper tools for attaching custom validation rule overrides directly to function parameters.

## Public Components Registry

| Component        | Type     | Description                                                                      |
| :--------------- | :------- | :------------------------------------------------------------------------------- |
| `override_rules` | Function | Helper for decorating parameters with custom Rule or predicate overrides.        |
"""