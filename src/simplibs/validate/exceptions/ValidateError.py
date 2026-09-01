from simplibs.exception import SimpleException


class ValidateError(SimpleException):
    """Root exception class for all errors originating from simplibs-validate.

    Serves as the single common ancestor (root exception) for every
    validation error raised within the system. Lets users catch any
    validation error from the library with a single except block:

        try:
            validate(value, rule)
        except ValidateError as e:
            ...
    """

    # Skips the library's internal frames when resolving the error's origin
    # location. This way, the diagnostic message points directly to the
    # user's own code, not to the library's internals.
    skip_locations = ("simplibs/validate",)


_DESIGN_NOTES = """
# ValidateError — Main Root Validation Exception

## Purpose
The `ValidateError` class forms the single, unified outward-facing exception
type for the entire `simplibs-validate` library. It inherits directly from
`SimpleException` in the `simplibs-exception` ecosystem.

---

## 1. Architectural Role & Design

### Single Catch-All Exception
* All specific rule exceptions or helper exceptions inherit from
  `ValidateError` (or use this class directly with the extra attributes
  `label`, `expected`, `problem`, `how_to_fix`).
* Thanks to this, library users don't need to import dozens of different
  exceptions — catching `ValidateError` is enough.

### Stack Trace Filtering (`skip_locations`)
* Setting `skip_locations = ("simplibs/validate",)` ensures that the
  diagnostic report from `simplibs-exception` marks the origin of the error
  as the line in the user's own codebase that triggered the validation, not
  the library's internals.

---

## 2. Notes
* This attribute must be named `skip_locations`, matching the field defined
  on `SimpleExceptionData` — not `_skip_locations`. An earlier revision used
  the underscored name, which `SimpleExceptionData` does not declare, so the
  filtering silently had no effect (or fails the anti-typo audit in
  `__init_subclass__`, depending on the exact check). Fixed here.
"""