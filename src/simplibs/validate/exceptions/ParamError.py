from .ValidateError import ValidateError


class ParamError(ValidateError):
    """Exception raised for invalid parameter or decorator configuration.

    Signals a developer error made while constructing validation rules or configuring
    decorators, as opposed to a `ValidationError`, which signals invalid input data.
    """

    pass


_DESIGN_NOTES = """
# ParamError — Developer Configuration Exception

## Purpose
The `ParamError` class is used to catch and format errors that arise from
invalid decorator configuration or passing invalid parameters into rule constructors.
It inherits directly from `ValidateError`.

---

## 1. Architectural Role

* **Inheritance from `ValidateError`:**
  Inherits stack-frame filtering and diagnostic card generation from `ValidateError`.
* **Semantic Distinction:**
  Lets users catch configuration errors (`except ParamError`) separately from data
  validation errors (`except ValidationError`).
"""