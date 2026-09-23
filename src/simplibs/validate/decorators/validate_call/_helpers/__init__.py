from .BYPASS_PARAM_NAME import BYPASS_PARAM_NAME
from .compile_parameter_rules import compile_parameter_rules
from .compile_return_rule import compile_return_rule
from .get_context_string import get_context_string
from .is_bypass_parameter import is_bypass_parameter
from .should_validate import should_validate
from .unwrap_validate_call import unwrap_validate_call


_DESIGN_NOTES = """
# Validate Call Internal Helpers Sub-Package

## Purpose
Internal compilation helpers used by `@validate_call` at decoration time to compile
signature type annotations and override rules into executable `Rule` pipelines, as
well as selective unwrapping utilities for pipeline normalization.

## Internal Components Registry

| Component                 | Type     | Description                                                                     |
| :------------------------ | :------- | :------------------------------------------------------------------------------ |
| `BYPASS_PARAM_NAME`       | Constant | Canonical string name of the reserved per-call bypass parameter ("_validate_call").|
| `compile_parameter_rules` | Function | Compiles parameter type annotations and custom overrides into a rule dictionary.|
| `compile_return_rule`     | Function | Compiles the return type annotation into a `Rule` if return validation is active.|
| `get_context_string`      | Function | Safely extracts formatted diagnostic context strings from target functions.     |
| `is_bypass_parameter`     | Function | Identifies whether a parameter is the reserved "_validate_call" per-call bypass flag.|
| `should_validate`         | Function | Evaluates at call time whether validation checks should run for a given call.   |
| `unwrap_validate_call`    | Function | Recursively strips existing `@validate_call` wrapper layers from a target function.|
"""