from simplibs.exception import SimpleException


class ValidateError(SimpleException):
    """Root exception class for all errors originating from simplibs-validate.

    Serves as the single common ancestor (root exception) for every error raised
    within the library. Lets users catch any error from the library with a single
    except block:

        try:
            ...
        except ValidateError as e:
            ...
    """

    # Skips the library's internal frames when resolving the error's origin
    # location. This way, the diagnostic message points directly to the
    # user's own code, not to the library's internals.
    skip_locations = ("simplibs/validate",)


_DESIGN_NOTES = """
# ValidateError — Root Library Exception

## Purpose
The `ValidateError` class forms the single, unified root exception type for the
entire `simplibs-validate` library. It inherits directly from `SimpleException`.

---

## 1. Architectural Role & Design

### Root Exception
* Serves purely as the abstract root exception for the library hierarchy.
* Specific subtypes (`ValidationError` for input data failures, `ParamError` for
  developer configuration errors) inherit directly from this class.
* Catching `ValidateError` catches any error originating from the library.

### Stack Trace Filtering (`skip_locations`)
* Setting `skip_locations = ("simplibs/validate",)` ensures that the
  diagnostic report from `simplibs-exception` marks the origin of the error
  as the line in the user's own codebase that triggered the failure.
"""