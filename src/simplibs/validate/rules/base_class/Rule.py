from abc import ABC, abstractmethod
from typing import Any, Callable, Annotated


class Rule(ABC):
    """Abstract base class for all validation rules.

    Every concrete rule inherits from this class and implements `is_valid` and `build_exception`.
    The class also provides a unified evaluation interface via `validate`, the magic `__call__` method,
    and Python typing integration via `annotated`.
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
    # 3) Typing Integration
    # ----------------------------------------------------------------------

    def annotated(self, type_: type) -> Any:
        """Wrap this rule as `typing.Annotated[type_, self]` for type hints.

        Enables seamless integration with static type checkers (MyPy, Pyright)
        and runtime annotation inspection (e.g., IsTyping or decorator engines).

        Args:
            type_: The target base type (e.g., int, str, float).

        Returns:
            An `Annotated` type hint combining the base type and this rule as metadata.
        """
        return Annotated[type_, self]

    # ----------------------------------------------------------------------
    # 4) Operator-Based Composition (|, &, ~)
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
evaluating conditions, assembling structured exceptions (`SimpleException`),
and bridging validation rules with Python's typing system.

---

## 1. Architectural Principles & Minimalism

### Single Responsibility
* **Evaluation Scope:** The `Rule` class is exclusively concerned with
  whether a value satisfies the condition (`is_valid`) and how the exception
  card looks on failure (`build_exception`).
* **`None` Value Handling:** The rule itself does not special-case `None`.
  If `None` needs to be treated as a valid value, compose it explicitly
  with `IsNone` (e.g. `rule | IsNone()`) rather than relying on a global
  flag.

### Zero Import-Time Overhead
* Unnecessary metaclass inspection routines have been removed in accordance with
  the **Programmer's Zen** philosophy. Documentation and usage examples are
  audited via automated unit tests rather than import-time hooks.

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

## 3. Typing System Integration (`annotated`)

### Purpose & Syntax Sugar

The `annotated(type_)` method bridges runtime validation rules directly into
Python's standard type annotation machinery via `typing.Annotated` (PEP 593).

```python
my_rule = is_integer & greater_than(0)

# Enables clean, fluent type definitions:
PositiveInt = my_rule.annotated(int)

def process_age(age: PositiveInt) -> None:
    ...

```

### Static vs. Runtime Dual-Benefit

* **Static Type Checkers (MyPy / Pyright / IDEs):** Treat `Annotated[T, metadata]`
transparently as `T`. Code passes type checking seamlessly as if plain `int`
or `str` was used.
* **Runtime Ecosystem (IsTyping & Decorators):** Inspection engines unpack
`Annotated` via `get_origin` and `get_args`, extracting `self` (the `Rule` instance)
from metadata to enforce validation rules dynamically.

---

## 4. Operator-Based Composition (`|`, `&`, `~`)

### Why These Three, and Not `and`/`or`/`not`

* Python's `and`, `or`, and `not` keywords cannot be overloaded.
* `|`, `&`, and `~` are the standard operators Python allows to be overloaded
for composable predicate objects.

### What Each Operator Does

* **`rule1 | rule2`** (`__or__` / `__ror__`) → `AnyOf(rule1, rule2)`.
* **`rule1 & rule2`** (`__and__` / `__rand__`) → `AllOf(rule1, rule2)`.
* **`~rule`** (`__invert__`) → `Not(rule)`.

### Design Choices

* **Lazy Imports:** Container imports (`AnyOf`, `AllOf`, `Not`) are deferred inside
method bodies to prevent circular import issues.
* **`NotImplemented` Fallback:** Binary operators return `NotImplemented` for unsupported
types, allowing Python's standard reflected operator protocols to execute naturally.

---

## 5. Ecosystem Integration

* **`simplibs-exception`:** `build_exception` utilizes `value_name` as `label`,
`context`, and `value` to format readable diagnostic cards.
* **`IsTyping` & `annotated_builder`:** Automatically extracts `Rule` instances attached
via `.annotated()` to decompose typing constructs into composed validation trees.
"""