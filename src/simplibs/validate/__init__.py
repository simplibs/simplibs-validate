"""Root package for simplibs-validate."""

# 1. Direct core module imports
from .validate import validate
from .raise_invalid import raise_invalid

# 2. Extract __all__ lists BEFORE star-imports
from .decorators import __all__ as _decorators_all
from .tools import __all__ as _tools_all
from .validators import __all__ as _validators_all

# 3. Re-export public members into root namespace
from .decorators import *
from .tools import *
from .validators import *

# 4. Assemble root __all__
__all__ = (
    ["validate", "raise_invalid"]
    + _decorators_all
    + _tools_all
    + _validators_all
)


_DESIGN_NOTES = r"""
# simplibs-validate — Root Package API Facade

## Purpose
The root `simplibs.validate` package acts as a unified top-level facade.
It re-exports all primary public decorators, helper tools, and high-level
functional type validators for maximum developer convenience.

## Sub-Packages Architecture Registry

| Sub-Package                    | Primary Focus | Re-exported at Root | Description                                                                 |
| :----------------------------- | :------------ | :------------------ | :-------------------------------------------------------------------------- |
| `simplibs.validate.decorators` | Decorators    | Yes                 | Core execution decorators (`validate_call`, `validate_dataclass`, etc.).    |
| `simplibs.validate.tools`      | Utilities     | Yes                 | Standalone tools (`override_rules`, `raise_invalid`, `validated_type`).     |
| `simplibs.validate.validators` | Function API  | Yes                 | Type-specific wrapper functions (`validate_int`, `validate_str`, etc.).     |
| `simplibs.validate.testing`    | Test Suite    | No                  | Assertion contracts and test utilities (excluded from root wildcard).       |
"""