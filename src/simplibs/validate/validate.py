from typing import Any, Callable
# Inners
from .rules.base_class import Rule
from .exceptions import build_validation_error


def validate(
    value: Any,
    rule: Rule | Callable[[Any], bool],
    *,
    value_name: str | None = None,
    context: str | None = None,
    return_bool: bool = False,
    return_value: bool = False,
) -> Any:
    """Validate a value against a `Rule` instance or any callable function (e.g., lambda).

    Serves as a universal entry point for single-use validations.
    Allows returning a boolean instead of raising an exception, or returning
    the original value upon success.

    Args:
        value: The tested value.
        rule: A rule instance inheriting from `Rule` or a callable object (e.g., lambda).
        value_name: The name of the validated variable/parameter for diagnostic reports.
        context: Additional context describing the validation environment.
        return_bool: If True, returns `False` on validation failure instead of raising an exception.
        return_value: If validation passes and this is True, returns the original `value` instead of `True`.

    Returns:
        Returns `value`, `True`, or `False` depending on the specified parameter flags.

    Raises:
        Exception: If validation fails and `return_bool` is False.
    """

    # 1. Rule instance handling — delegate entirely to Rule.validate()
    if isinstance(rule, Rule):
        return rule.validate(
            value,
            value_name=value_name,
            context=context,
            return_bool=return_bool,
            return_value=return_value,
        )

    # 2. Callable handling (plain function / lambda)
    # 2.1 Validation execution and success handling
    if rule(value):
        return value if return_value else True

    # 2.2 Return bool handling
    if return_bool:
        return False

    # 2.3 Failure handling
    raise build_validation_error(
        rule,
        value,
        value_name=value_name,
        context=context,
    )


_DESIGN_NOTES = """
# validate — Primary Validation Orchestrator

## Purpose
The `validate()` function eliminates the need for manual condition checking
and exception raising boilerplate. It unifies the validation interface across
official `Rule` objects, ad-hoc user functions, and anonymous expressions
(`lambda`).

---

## 1. Execution Pipeline

1. **`Rule` Instance Handling:**
   * Delegates entirely to `rule.validate(...)`, forwarding every parameter
     as-is. `validate()` does not re-implement any of the pass/fail/return
     logic for `Rule` instances — that logic has exactly one home,
     `Rule.validate()`, and this function is a thin pass-through to it.

2. **Callable Handling (plain function / lambda):**
   * Capitalizes on the fact that a plain function/lambda is directly
     callable with `value`.
   * Evaluates the truthiness of the return value (not a strict `bool`
     check — see "No Contract Enforcement on User Callables" below).
   * On success, returns either `value` (if `return_value=True`) or `True`.
   * On failure: `return_bool=True` returns `False`; otherwise raises a
     structured exception via `build_validation_error()`.

---

## 2. Design Choices & Rationale

### Delegation Over Duplication for `Rule` Instances
* An earlier revision inlined `Rule.validate()`'s own pass/fail/return
  logic directly inside this function (calling `rule.is_valid(value)` and
  `rule.build_exception(...)` here, instead of `rule.validate(...)`). That
  was considered and rejected: `validate()` is a top-level entry point
  called once per validation, not a hot inner loop, so the saved function
  call is on the order of tens of nanoseconds — below any measurable
  threshold — while duplicating the branching logic in two places creates
  a real, ongoing maintenance cost (a future change to the return-mode
  logic would need to be kept in sync in both places). Delegating to
  `rule.validate()` keeps that logic in exactly one place.
* This is a deliberately different call site from `as_predicate()` (used
  inside container rules like `AllOf`/`ForEach`), which *does* bypass
  `__call__` in favor of a direct `is_valid` binding — there, the same
  rule is evaluated potentially thousands of times per call, so the same
  nanosecond-scale saving actually compounds into something measurable.
  No such loop exists here.

### No Contract Enforcement on User Callables
* For a plain callable, `validate()` does not verify that it returns a
  strict `bool`, and does not catch exceptions it might raise. The
  callable is invoked directly and its outcome (or failure) is trusted
  as-is — the same way any user-supplied function is normally called in
  Python.
* This is intentional, not an oversight: `Rule` subclasses carry an
  explicit contract (`is_valid` must always return strictly `True`/`False`
  and must never raise), which this library enforces and relies on
  throughout (containers, `as_predicate`, ...). A plain user callable
  carries no such contract, and `validate()` does not attempt to impose
  one after the fact:
  * Wrapping the call in `isinstance(outcome, bool)` enforcement would be
    a breaking behavioral change — any existing callable relying on
    ordinary Python truthiness (e.g. `lambda x: x`, returning a truthy/
    falsy non-bool) would suddenly fail differently.
  * Catching and re-wrapping exceptions raised by the callable (e.g. into
    a generic "unexpected error") would destroy the original traceback
    and diagnostic detail — a real bug inside the user's own callable
    (say, an `AttributeError` from mishandling `value`'s type) is more
    useful to the caller surfaced as-is than hidden behind a repackaged
    `simplibs-validate` error.
* In short: `validate()` guarantees the contract for `Rule` objects (since
  it owns that contract), and simply runs — without inspecting, coercing,
  or protecting against — anything else.

### Direct Integration of `build_validation_error`
* Converting callable failures into structured exceptions is concise and
  single-purpose, making it an ideal fit for direct delegation from this
  orchestrator module.
"""
