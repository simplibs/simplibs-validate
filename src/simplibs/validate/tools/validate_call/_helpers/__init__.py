from .compile_parameter_rules import compile_parameter_rules
from .compile_return_rule import compile_return_rule
from .get_context_string import get_context_string
from .is_bypass_parameter import is_bypass_parameter
from .should_validate import should_validate


_DESIGN_NOTES = """
# Validate Call Internal Helpers Sub-Package

## Purpose
Internal compilation helpers used by `@validate_call` at decoration time to compile
signature type annotations and override rules into executable `Rule` pipelines.

## Internal Components Registry

| Component                 | Type     | Description                                                                     |
| :------------------------ | :------- | :------------------------------------------------------------------------------ |
| `compile_parameter_rules` | Function | Compiles parameter type annotations and custom overrides into a rule dictionary.|
| `compile_return_rule`     | Function | Compiles the return type annotation into a `Rule` if return validation is active.|
| `get_context_string`      | Function | Safely extracts formatted diagnostic context strings from target functions.     |
| `is_bypass_parameter`     | Function | Identifies whether a parameter is the reserved "validate" per-call bypass flag.|
| `should_validate`         | Function | Evaluates at call time whether validation checks should run for a given call.   |
"""