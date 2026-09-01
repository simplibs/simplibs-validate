from typing import Any, Collection, Container
# Outers
from ...base_class import Rule
from ....exceptions import ValidateError
from ..collections.IsContainer import is_container
from .._init_validators import raise_param_not_container_error
from .._helpers import format_container


class IsIn(Rule):
    """Value must be a member of the given collection.

    Rule:
        value in options

    Example:
        validate(value, IsIn(("draft", "published", "archived")))
    """

    __slots__ = ("options",)

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, options: Container[Any]) -> None:

        # 1. Handle invalid input type error
        if not is_container(options):
            raise_param_not_container_error("IsIn", "options", options)

        # 2. Store the parameter
        self.options = options

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate membership in the collection
        try:
            return value in self.options

        # 2. Fallback for incomparable input
        except TypeError:
            return False

    # ----------------------------------------------------------------------
    # Exception definition
    # ----------------------------------------------------------------------
    def build_exception(
        self,
        value: Any,
        value_name: str | None = None,
        context: str | None = None,
    ) -> Exception:

        # 1. Format the collection representation deterministically
        opts_repr = format_container(self.options)
        if len(opts_repr) > 60:
            opts_repr = f"{type(self.options).__name__}(size={len(self.options)})"

        # 2. Prepare data
        try:
            # Test whether the value can even be looked up in the collection
            _ = value in self.options

            # 2.1 When the value is lookup-able, but missing from the collection
            problem = f"Value {value!r} is not one of {opts_repr}."
            how_to_fix = f"Provide a value contained in {opts_repr}."
            exception_type = ValueError

        except TypeError:
            # 2.2 When the value is unhashable (e.g. a list in a set/dict)
            problem = (
                f"Value {value!r} of type '{type(value).__name__}' cannot be looked up "
                f"in container '{type(self.options).__name__}'."
            )
            how_to_fix = "Provide a hashable value (e.g. tuple instead of list) or a compatible container."
            exception_type = TypeError

        # 3. Build the exception
        return ValidateError(
            error_name="IS_IN_ERROR",
            label=value_name,
            expected=f"one of {opts_repr}",
            value=value,
            problem=problem,
            context=context,
            how_to_fix=how_to_fix,
            exception=exception_type,
        )


_DESIGN_NOTES = """
# IsIn — Collection Membership Rule

## Purpose
The `IsIn` rule checks whether a given input value is contained within a
specific set or sequence of allowed options.

---

## 1. Execution Rationale & Safeguards

* **Constructor Fail-Fast:**
  Restricts `options` to standard collection data structures (`list`,
  `tuple`, `set`, `frozenset`, `dict`), throwing `ParamError` for
  non-container types (like strings or single integers) to prevent logic
  errors.
* **TypeError Safety (`is_valid`):**
  Uses a `try/except TypeError` block to cleanly handle cases where
  unhashable objects are searched inside sets/dicts or incomparable
  elements are checked.
* **Deterministic Set Representation:**
  Uses a helper `format_container` function during exception building to sort
  set elements before string formatting. This eliminates non-deterministic hash
  ordering when `set` or `frozenset` options are provided.
* **Representation Truncation:**
  If the container has a large string representation (> 60 characters),
  `build_exception()` abbreviates it to its container type and element
  size for clean output readability.

---

## 2. Exception Card Design

* **Error Classification:** Uses `IS_IN_ERROR` wrapping a `ValueError`.
* **Fix Guidance:** Displays expected member collection options clearly.
"""