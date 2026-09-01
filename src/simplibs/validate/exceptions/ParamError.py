from .ValidateError import ValidateError


class ParamError(ValidateError):
    """Exception raised for invalid parameter configuration in a rule's `__init__`.

    Signals a developer error made while constructing validation rules, as
    opposed to a regular `ValidateError`, which signals invalid input data.
    """

    pass


_DESIGN_NOTES = """
# ParamError — Developer Configuration Exception

## Purpose
The `ParamError` class is used to catch and format errors that arise from
passing invalid parameters into the constructors (`__init__`) of rule
classes. It inherits directly from `ValidateError`.

---

## 1. Architectural Role

* **Inheritance from `ValidateError`:**
  Inherits the full diagnostic card behavior of `SimpleException`, including
  automatic skipping of the library's internal frames (`skip_locations`).
* **Semantic Distinction:**
  Lets advanced users or test suites explicitly catch rule-configuration
  errors (`except ParamError`) separately from data errors
  (`except ValidateError`).
"""