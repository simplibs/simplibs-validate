"""Root package for simplibs-validate."""

# 1. Direct core module imports
from .raise_invalid import raise_invalid
from .validate import validate

# 2. Extract __all__ lists BEFORE star-imports (prevents SimpleNamespace shadow overriding)
from .exceptions import __all__ as _exceptions_all
from .rules import __all__ as _rules_all
from .tools import __all__ as _tools_all
from .validators import __all__ as _validators_all

# 3. Re-export public members into root namespace
from .exceptions import *
from .rules import *
from .tools import *
from .validators import *

# 4. Assemble root __all__
__all__ = (
    ["validate", "raise_invalid"]
    + _exceptions_all
    + _rules_all
    + _tools_all
    + _validators_all
)


_DESIGN_NOTES = r"""
# simplibs-validate — Root Package API Facade

## Purpose
The root `simplibs.validate` package acts as a unified top-level facade. It re-exports
all primary public components across exceptions, rule shortcuts/classes, decorators, 
and high-level type validators for maximum developer convenience.

## Sub-Packages Architecture Registry

| Sub-Package                   | Primary Focus | Re-exported at Root | Description                                                                 |
| :---------------------------- | :------------ | :------------------ | :-------------------------------------------------------------------------- |
| `simplibs.validate.exceptions` | Exceptions    | Yes                 | Exception hierarchy (`ValidateError`, `ValidationError`, `ParamError`).      |
| `simplibs.validate.rules`      | Rules Engine  | Yes                 | Validation rules, rule shortcuts, and operator compositions (`&`, `\|`, `~`).|
| `simplibs.validate.tools`      | Decorators    | Yes                 | Core decorators (`validate_call`, `validate_dataclass`, `log_this`).        |
| `simplibs.validate.validators` | Function API  | Yes                 | Type-specific functions (`validate_int`, `validate_string`, etc.).          |
| `simplibs.validate.testing`    | Test Suite    | No                  | Assertion contracts and test utilities (excluded from root wildcard).       |
"""