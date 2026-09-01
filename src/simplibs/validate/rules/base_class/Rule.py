from abc import ABC, abstractmethod
from typing import Any, Callable


class Rule(ABC):
    """Abstract base class for all validation rules.

    Every concrete rule inherits from this class and implements `is_valid` and `build_exception`.
    The class also provides a unified evaluation interface via `validate` and the magic `__call__` method.
    """

    # ----------------------------------------------------------------------
    # 1) Abstract Interface (mandatory for subclasses)
    # ----------------------------------------------------------------------

    @abstractmethod
    def is_valid(
        self,
        value: Any,
    ) -> bool:
        """Return True if the tested value satisfies the rule, otherwise False."""
        raise NotImplementedError

    @abstractmethod
    def build_exception(
        self,
        value: Any,
        value_name: str | None = None,
        context: str | None = None,
    ) -> Exception:
        """Create and return an exception instance (SimpleException) describing the validation failure."""
        raise NotImplementedError

    # ----------------------------------------------------------------------
    # 2) Public Interface & Evaluation Logic
    # ----------------------------------------------------------------------

    def __call__(
        self,
        value: Any,
    ) -> bool:
        """Allow using the rule instance directly as a predicate function.

        Returns the boolean result of `is_valid(value)`.
        """
        return self.is_valid(value)

    def validate(
        self,
        value: Any,
        *,
        value_name: str | None = None,
        context: str | None = None,
        return_bool: bool = False,
        return_value: bool = False,
    ) -> Any:
        """Validate a value against this rule.

        Based on parameter flags, returns the original value, True/False,
        or raises a structured exception constructed by `build_exception`.

        Args:
            value: The tested value.
            value_name: The name of the validated parameter/variable for diagnostic reporting.
            context: Additional context describing the validation environment.
            return_bool: If True, returns False on failure instead of raising an exception.
            return_value: If validation passes and this is True, returns original `value` instead of `True`.

        Returns:
            Returns `value`, `True`, or `False` depending on parameter flags.

        Raises:
            Exception: If validation fails and `return_bool` is False.
        """
        if self.is_valid(value):
            return value if return_value else True

        if return_bool:
            return False

        raise self.build_exception(
            value,
            value_name=value_name,
            context=context,
        )

    # ----------------------------------------------------------------------
    # 3) Operator-Based Composition (|, &, ~)
    # ----------------------------------------------------------------------

    def __or__(self, other: "Rule | Callable[[Any], bool]") -> "Rule":
        """Combine with another rule/callable via logical OR: `rule1 | rule2`.

        Equivalent to `AnyOf(self, other)`. Returns `NotImplemented` if `other`
        is neither a `Rule` instance nor a plain callable, letting Python fall
        back to `other.__ror__(self)` or raise `TypeError` as usual.
        """
        if not (isinstance(other, Rule) or callable(other)):
            return NotImplemented

        from ..containers.AnyOf import AnyOf
        return AnyOf(self, other)

    def __ror__(self, other: "Rule | Callable[[Any], bool]") -> "Rule":
        """Support `other | rule` when `other` has no (or a declining) `__or__`."""
        if not (isinstance(other, Rule) or callable(other)):
            return NotImplemented

        from ..containers.AnyOf import AnyOf
        return AnyOf(other, self)

    def __and__(self, other: "Rule | Callable[[Any], bool]") -> "Rule":
        """Combine with another rule/callable via logical AND: `rule1 & rule2`.

        Equivalent to `AllOf(self, other)`. Returns `NotImplemented` if `other`
        is neither a `Rule` instance nor a plain callable, letting Python fall
        back to `other.__rand__(self)` or raise `TypeError` as usual.
        """
        if not (isinstance(other, Rule) or callable(other)):
            return NotImplemented

        from ..containers.AllOf import AllOf
        return AllOf(self, other)

    def __rand__(self, other: "Rule | Callable[[Any], bool]") -> "Rule":
        """Support `other & rule` when `other` has no (or a declining) `__and__`."""
        if not (isinstance(other, Rule) or callable(other)):
            return NotImplemented

        from ..containers.AllOf import AllOf
        return AllOf(other, self)

    def __invert__(self) -> "Rule":
        """Negate this rule via `~rule`. Equivalent to `Not(self)`."""
        from ..containers.Not import Not
        return Not(self)


_DESIGN_NOTES = """
# Rule — Base Abstract Class for Validation Rules

## Purpose
The `Rule` class serves as the fundamental pillar of the entire
`simplibs-validate` library. It defines a standardized interface for
evaluating conditions and assembling structured exceptions
(`SimpleException`).

---

## 1. Architectural Principles & Minimalism

### Single Responsibility
* **Evaluation Scope:** The `Rule` class is exclusively concerned with
  whether a value satisfies the condition (`is_valid`) and how the exception
  card looks on failure (`build_exception`).
* **`None` Value Handling:** The rule itself does not special-case `None`.
  If `None` needs to be treated as a valid value, compose it explicitly
  with `IsNone` (e.g. `rule | IsNone()`) rather than relying on a global
  flag — see the "Removed `accept_none`" note in `validate()`'s design
  notes for the full rationale.

### Zero Import-Time Overhead
* Unnecessary metaclass inspection routines (`__init_subclass__` docstring
  regexes) have been removed in accordance with the **Programmer's Zen**
  philosophy. Documentation and usage examples are audited via automated
  unit tests rather than import-time hooks.

---

## 2. Core Methods

### `is_valid(value) -> bool`
* Pure abstract method.
* Must never raise exceptions for standard validation failures—always
  returns strictly `True` or `False`.

### `build_exception(value, value_name, context) -> Exception`
* Constructs and returns an exception instance (typically from the
  `simplibs-exception` family).
* The exception is only **assembled and returned**, not raised directly in
  this method.

### `__call__(value) -> bool`
* Callable magic method enabling direct predicate invocation:
  ```python
  rule = IS_INTEGER()
  if rule(5):
      ...
  ```

### `validate(value, ...)`
* Primary evaluation method offering a flexible return interface:
  1. Value passes & `return_value=True` → returns `value`.
  2. Value passes & `return_value=False` → returns `True`.
  3. Value fails & `return_bool=True` → returns `False`.
  4. Value fails & `return_bool=False` → raises exception from
     `build_exception(...)`.

---

## 3. Operator-Based Composition (`|`, `&`, `~`)

### Why These Three, and Not `and`/`or`/`not`/`all`/`any`
* Python's `and`, `or`, and `not` keywords cannot be overloaded — they
  always resolve through truthiness (`__bool__`) and always return one of
  the original operands (or `True`/`False`), never a custom object. There
  is no way to make `rule1 or rule2` return an `AnyOf(...)` instance.
* `all()`/`any()` operate over an iterable of already-evaluated truthy
  values, not over `Rule` objects themselves. Giving `Rule` a `__bool__`
  so that `any([rule1, rule2])` "worked" would be actively misleading — a
  `Rule` has no truth value of its own until it is evaluated against a
  concrete `value`. The existing usage inside container rules, e.g.
  `any(as_predicate(rule)(value) for rule in rules)`, is `any()` over
  *evaluation results*, which is the correct and only sensible use.
* `|`, `&`, and `~` are the operators Python actually allows to be
  overloaded for this purpose, and match an established convention for
  composable predicate/filter objects (e.g. Django's `Q() | Q()`,
  pandas boolean masks).

### What Each Operator Does
* **`rule1 | rule2`** (`__or__` / `__ror__`) → `AnyOf(rule1, rule2)`.
* **`rule1 & rule2`** (`__and__` / `__rand__`) → `AllOf(rule1, rule2)`.
* **`~rule`** (`__invert__`) → `Not(rule)`.

### Design Choices
* **Lazy Imports:** `AnyOf`, `AllOf`, and `Not` live in
  `rules.containers`, which itself imports `Rule` from `base_class` — a
  module-level import here would create a circular import. Each operator
  method imports its target container lazily, inside the method body, so
  the cost (and the cycle) only exists at the moment an operator is
  actually used, consistent with this class's "Zero Import-Time Overhead"
  principle above.
* **`NotImplemented`, Not a Raised Error:** Every binary operator returns
  `NotImplemented` (not `False`, not an exception) when `other` is neither
  a `Rule` nor a plain callable. This lets Python fall back to `other`'s
  own reflected method, or raise a standard `TypeError` if neither side
  can handle it — the normal, expected Python protocol for operator
  overloading, rather than a `simplibs-validate`-specific error.
* **Reflected Methods (`__ror__`, `__rand__`) Matter:**
  Plain functions and lambdas have no `__or__`/`__and__` of their own, so
  an expression like `some_lambda | rule` only works because Python falls
  back to `rule.__ror__(some_lambda)`. Both directions are implemented so
  composition reads naturally regardless of which operand is the `Rule`.
* **Flattening Lives in the Containers, Not Here:**
  Chaining, e.g. `a | b | c`, evaluates left-to-right as
  `(a | b) | c`, which would naively nest as `AnyOf(AnyOf(a, b), c)`.
  Rather than special-casing that here, `AnyOf`/`AllOf` flatten
  same-type nested instances in their own constructors — see their design
  notes — so this stays a pure one-line delegation.
* **Compatible With Future Zero-Arg Instances:**
  This design composes equally well whether both sides are already-built
  `Rule` instances (`IsInteger() | IsNone()`) or, per a planned future
  change, pre-instantiated zero-parameter singletons exposed at module
  level (`is_instance(int) | is_none`) — operator resolution only cares
  that each operand is a `Rule` (or callable), not how it was constructed.

---

## 4. Ecosystem Integration

* **`simplibs-exception`:** `build_exception` utilizes `value_name` as
  `label`, `context`, and `value` to format readable diagnostic cards.
* **`validate()` Standalone Function:** Delegates execution to
  `rule.validate()` or handles callable fallbacks seamlessly.
"""
