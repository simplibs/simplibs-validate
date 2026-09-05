from .ValidateError import ValidateError


class ValidationError(ValidateError):
    """Exception raised when input data fails validation against a Rule.

    Signals an invalid data value supplied at runtime (e.g., invalid function
    arguments or invalid dataclass field values).
    """

    pass


_DESIGN_NOTES = """
# ValidationError — Data Validation Exception

## Purpose
The `ValidationError` class is raised whenever runtime data fails to satisfy a
`Rule`. It inherits directly from `ValidateError`.

---

## 1. Architectural Role

* **Inheritance from `ValidateError`:**
  Inherits stack-frame filtering and diagnostic card generation from `ValidateError`.
* **Semantic Distinction:**
  Allows users to catch runtime input failures (`except ValidationError`) separately
  from developer configuration mistakes (`except ParamError`).
"""