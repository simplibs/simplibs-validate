# ⚖️ `simplibs-validate`

[![PyPI](https://img.shields.io/pypi/v/simplibs-validate)](https://pypi.org/project/simplibs-validate/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![Licence](https://img.shields.io/badge/licence-MIT-green)](https://github.com/simplibs/simplibs-validate/blob/main/LICENSE)

**Composable, explicit validation — no magic, no data transformation, just answers.**

A lightweight Python library for validating values against rules built from small,
single-purpose predicate classes. Rules compose with plain operators (`|`, `&`, `~`),
carry structured, human-readable diagnostics on failure, and — through `IsTyping` —
understand your existing type annotations directly, so a whole function's inputs can
be validated automatically from its own signature.

```python
from simplibs.validate import validate, is_integer, greater_than

validate(5, is_integer & greater_than(0))          # -> True
validate(-5, is_integer & greater_than(0))          # -> raises ValidationError
```

---

## 🧭 The Core Philosophy

Most validation approaches force a choice: either write ad-hoc `if`/`raise` checks
scattered through your codebase, or adopt a heavy framework that also wants to parse,
coerce, and serialize your data along the way. `simplibs-validate` is neither — it's a
**pure predicate engine**. A `Rule` never transforms a value; it only ever answers "does
this satisfy me?" and, on failure, explains exactly why.

Every rule is a small, composable object. Combine them with plain Python operators
instead of nested configuration:

```python
is_string & has_length(min_length=3) & not_blank
```

And because rules already understand Python's own typing system, the same machinery
that powers `validate()` also powers `@validate_call` — a decorator that validates an
entire function's arguments straight from its type hints, no separate schema to
maintain:

```python
from simplibs.validate import validate_call, validated_type

PositiveInt = validated_type(int, greater_than(0))

@validate_call
def register(age: PositiveInt, *, validate: bool = True) -> None:
    ...

register(25)                       # validated normally
register(-5)                       # raises ValidationError
register(-5, validate=False)       # explicitly skipped — e.g. already validated upstream
```

That combination — annotation-driven rules, a decorator that enforces them
automatically, and a per-call opt-out for code paths that already trust their data —
is what lets you build fully self-validating functions and dataclasses from nothing
more than their own signatures.

---

## 📦 Installation

```bash
pip install simplibs-validate
```

---

## 🚀 Quick Start in 60 Seconds

### Level 1: One-off validation

```python
from simplibs.validate import validate, is_integer, greater_than

validate(5, is_integer & greater_than(0))
validate(5, is_integer & greater_than(0), return_bool=True)   # -> True, no exception
validate("x", is_integer, return_bool=True)                    # -> False, no exception
```

### Level 2: Ready-made validators

Every common type has a batteries-included `validate_*` function, taking the
constraint as plain keyword arguments — no rule composition required:

```python
from simplibs.validate import validate_string, validate_int

validate_string("user@example.com", contains="@", min_length=5)
validate_int(42, greater_than=0, divisible_by=2)
```

### Level 3: Annotation-driven, self-validating functions

```python
from simplibs.validate import validate_call

@validate_call
def create_user(name: str, age: int) -> dict:
    return {"name": name, "age": age}

create_user("Alice", 30)      # validated automatically from the annotations
create_user("Alice", "30")    # raises ValidationError
```

---

## 🛠️ The Architecture: 3 Layers

```
┌─────────────────────────┐
│          Rules          │ ◄── Rule subclasses + snake_case shortcuts
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│       Validators        │ ◄── validate_string, validate_int, ... presets
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│          Tools          │ ◄── validate_call, validate_dataclass, log_this, ...
└─────────────────────────┘
```

### 1. `validate` — the universal entry point

Every validation ultimately goes through one of two functions:

* **`validate(value, rule, ...)`** — evaluates `rule` against `value`, then either
  returns (`True`/the value) or raises, depending on the flags given. Use this
  everywhere you actually need the check performed.
* **`raise_invalid(value, rule, ...)`** — unconditionally builds and raises the
  diagnostic exception for `rule`, without evaluating anything. Use this where your
  own code has *already* determined a value is invalid (e.g. inside an `if not
  condition:` branch) and you just want the same structured `ValidateError` card
  `validate()` would have produced, without redundantly re-running the check.

```python
def validate(
    value: Any,
    rule: Rule | Callable[[Any], bool],
    *,
    value_name: str | None = None,
    context: str | None = None,
    return_bool: bool = False,
    return_value: bool = False,
) -> Any:

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

```

```python
def raise_invalid(
    value: Any,
    rule: Rule | Callable[[Any], bool],
    *,
    value_name: str | None = None,
    context: str | None = None,
) -> NoReturn:
  
    # 1. Rule instance handling
    if isinstance(rule, Rule):
        raise rule.build_exception(
            value,
            value_name=value_name,
            context=context,
        )

    # 2. Callable handling (plain function / lambda)
    raise build_validation_error(
        rule,
        value,
        value_name=value_name,
        context=context,
    )
```

Both accept either a `Rule` instance or a plain callable predicate — a `Rule` delegates
to its own `validate()`/`build_exception()`, while a callable is evaluated directly and,
on failure, wrapped in a generic diagnostic via `build_validation_error`.

### 2. Specialized validators

For the most common types, a ready-made `validate_*` function exposes every relevant
constraint as a plain keyword argument, composing the equivalent `Rule` tree
internally — no manual `&`-chaining required for everyday cases.

| Validator            | Description                                                                                | Docs                                                                                                                              |
|----------------------|--------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------|
| `validate_bool`      | Boolean, optionally against an exact expected value.                                       | [README_VALIDATE_BOOL](https://github.com/simplibs/simplibs-validate/blob/main/docs/validators/README_VALIDATE_BOOL.md)           |
| `validate_container` | Any non-string container — length, uniqueness, membership, subset/superset, per-item rule. | [README_VALIDATE_CONTAINER](https://github.com/simplibs/simplibs-validate/blob/main/docs/validators/README_VALIDATE_CONTAINER.md) |
| `validate_float`     | Float — comparisons, range, approximate equality, finiteness.                              | [README_VALIDATE_FLOAT](https://github.com/simplibs/simplibs-validate/blob/main/docs/validators/README_VALIDATE_FLOAT.md)         |
| `validate_int`       | Integer — comparisons, range, divisibility, remainder.                                     | [README_VALIDATE_INT](https://github.com/simplibs/simplibs-validate/blob/main/docs/validators/README_VALIDATE_INT.md)             |
| `validate_mapping`   | `dict` — length, single/multiple key membership.                                           | [README_VALIDATE_MAPPING](https://github.com/simplibs/simplibs-validate/blob/main/docs/validators/README_VALIDATE_MAPPING.md)     |
| `validate_number`    | Any number (`int`/`float`/`Decimal`/`complex`) — comparisons, range, membership.           | [README_VALIDATE_NUMBER](https://github.com/simplibs/simplibs-validate/blob/main/docs/validators/README_VALIDATE_NUMBER.md)       |
| `validate_string`    | String — length, prefix/suffix/substring, regex, blankness, membership.                    | [README_VALIDATE_STRING](https://github.com/simplibs/simplibs-validate/blob/main/docs/validators/README_VALIDATE_STRING.md)       |
| `validate_type`      | Class/type object — subclass, identity, membership.                                        | [README_VALIDATE_TYPE](https://github.com/simplibs/simplibs-validate/blob/main/docs/validators/README_VALIDATE_TYPE.md)           |

Each `validate_*` is a thin wrapper: it composes its matching `*_rule(...)` factory and
calls `.validate()` on the result. For repeated validation against the same
constraints, build the rule once with `*_rule(...)` and reuse it, instead of calling
`validate_*` inside a loop.

---

## 🧩 The `Rule` Class

Every validation in this library, from the simplest type check to the most elaborate
composed constraint, is a `Rule`. It defines the minimal contract every concrete rule
implements (`is_valid`, `build_exception`), and builds a full evaluation interface on
top of it: `validate()`, the callable shorthand (`rule(value)`), operator composition
(`|`, `&`, `~`), and `annotated()` — the bridge into Python's own typing system.

```python
class Rule(ABC):
  
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
        """Allow using the rule instance directly as a predicate function."""
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
        """Validate a value against this rule."""
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
        """Wrap this rule as `typing.Annotated[type_, self]` for type hints."""
        return Annotated[type_, self]

    # ----------------------------------------------------------------------
    # 4) Operator-Based Composition (|, &, ~)
    # ----------------------------------------------------------------------

    def __or__(self, other: "Rule | Callable[[Any], bool]") -> "Rule":
        """Combine with another rule/callable via logical OR: `rule1 | rule2`."""
        return AnyOf(self, other)

    def __ror__(self, other: "Rule | Callable[[Any], bool]") -> "Rule":
        """Support `other | rule` when `other` has no (or a declining) `__or__`."""
        return AnyOf(other, self)

    def __and__(self, other: "Rule | Callable[[Any], bool]") -> "Rule":
        """Combine with another rule/callable via logical AND: `rule1 & rule2`."""
        return AllOf(self, other)

    def __rand__(self, other: "Rule | Callable[[Any], bool]") -> "Rule":
        """Support `other & rule` when `other` has no (or a declining) `__and__`."""
        return AllOf(other, self)

    def __invert__(self) -> "Rule":
        """Negate this rule via `~rule`. Equivalent to `Not(self)`."""
        return Not(self)
```

➡️ Full method-by-method reference: [README_RULE_CLASS](https://github.com/simplibs/simplibs-validate/blob/main/docs/rules/README_RULE_CLASS.md)

---

## 📖 Rule Quick Reference

Every built-in `Rule` is exposed two ways: as its **class** (`IsInteger`), and as a
**snake_case shortcut** (`is_integer`) — a pre-instantiated object for zero-parameter
rules, or the class itself for parameterized ones. Both are fully interchangeable and
compose identically with `|`/`&`/`~`.

```python
validate(value, is_integer & greater_than(0))
# is exactly equivalent to:
validate(value, IsInteger() & GreaterThan(0))
```

Every rule below also has a `rule_class.<Name>` entry (for `isinstance` checks,
subclassing, or programmatic construction) and a `rules.<shortcut>` namespace entry —
both point at the same underlying object/class as the direct import.

### `containers/` — composing other rules

| Class     | Shortcut   | Params                                                                               |
|-----------|------------|--------------------------------------------------------------------------------------|
| `AllOf`   | `all_of`   | `*rules: Union[Rule, Callable[[Any], bool]]`                                         |
| `AnyOf`   | `any_of`   | `*rules: Union[Rule, Callable[[Any], bool]]`                                         |
| `Compose` | `compose`  | `transformer: Callable[[Any], Any]`, `validator: Union[Rule, Callable[[Any], bool]]` |
| `ForEach` | `for_each` | `rule: Union[Rule, Callable[[Any], bool]]`                                           |
| `NoneOf`  | `none_of`  | `*rules: Union[Rule, Callable[[Any], bool]]`                                         |
| `Not`     | `negate`   | `rule: Callable[[Any], bool]`                                                        |

➡️ [README_RULE_CONTAINERS](https://github.com/simplibs/simplibs-validate/blob/main/docs/rules/README_RULE_CONTAINERS.md)

### `predicates/arithmetic/` — numeric relationships

| Class          | Shortcut        | Params                                                                             |
|----------------|-----------------|------------------------------------------------------------------------------------|
| `CloseTo`      | `close_to`      | `target: Union[float, int]`, `*`, `rel_tol: float  = 1e-9`, `abs_tol: float = 0.0` |
| `DivisibleBy`  | `divisible_by`  | `divisor: int`                                                                     |
| `HasRemainder` | `has_remainder` | `divisor: int`, `remainder: int`                                                   |

➡️ [README_RULE_PREDICATE_ARITHMETIC](https://github.com/simplibs/simplibs-validate/blob/main/docs/rules/README_RULE_PREDICATE_ARITHMETIC.md)

### `predicates/checkers/` — basic state & identity

| Class      | Shortcut    | Params |
|------------|-------------|--------|
| `IsEmpty`  | `is_empty`  | `-`    |
| `IsFalse`  | `is_false`  | `-`    |
| `IsNone`   | `is_none`   | `-`    |
| `IsTrue`   | `is_true`   | `-`    |
| `NotEmpty` | `not_empty` | `-`    |

➡️ [README_RULE_PREDICATE_CHECKERS](https://github.com/simplibs/simplibs-validate/blob/main/docs/rules/README_RULE_PREDICATE_CHECKERS.md)

### `predicates/collections/` — containers, mappings & iterables

| Class          | Shortcut         | Params                       |
|----------------|------------------|------------------------------|
| `AllUnique`    | `all_unique`     | `-`                          |
| `HasItem`      | `has_item`       | `item: Any`                  |
| `HasKey`       | `has_key`        | `key: Any`                   |
| `HasKeys`      | `has_keys`       | `*keys: Any`                 |
| `IsContainer`  | `is_container`   | `-`                          |
| `IsSubsetOf`   | `is_subset_of`   | `reference: Collection[Any]` |
| `IsSupersetOf` | `is_superset_of` | `reference: Collection[Any]` |

➡️ [README_RULE_PREDICATE_COLLECTIONS](https://github.com/simplibs/simplibs-validate/blob/main/docs/rules/README_RULE_PREDICATE_COLLECTIONS.md)

### `predicates/comparisons/` — ordering & equality

| Class            | Shortcut(s)              | Params                                                                                 |
|------------------|--------------------------|----------------------------------------------------------------------------------------|
| `Equals`         | `equals`, `eq`           | `expected_value: Any`                                                                  |
| `NotEquals`      | `not_equals`, `ne`       | `forbidden: Any`                                                                       |
| `GreaterThan`    | `greater_than`, `gt`     | `threshold: Any`                                                                       |
| `GreaterOrEqual` | `greater_or_equal`, `ge` | `threshold: Any`                                                                       |
| `LessThan`       | `less_than`, `lt`        | `threshold: Any`                                                                       |
| `LessOrEqual`    | `less_or_equal`, `le`    | `threshold: Any`                                                                       |
| `InRange`        | `in_range`               | `min_val: Any`, `max_val: Any`, `include_min: bool = True`, `include_max: bool = True` |

➡️ [README_RULE_PREDICATE_COMPARISONS](https://github.com/simplibs/simplibs-validate/blob/main/docs/rules/README_RULE_PREDICATE_COMPARISONS.md)

### `predicates/introspection/` — structural & reflective checks

| Class          | Shortcut(s)                 | Params                                                                        |
|----------------|-----------------------------|-------------------------------------------------------------------------------|
| `IsInstance`   | `is_instance`               | `*types: type`                                                                |
| `IsType`       | `is_type`                   | `-`                                                                           |
| `IsSubclass`   | `is_subclass`               | `*types: type`                                                                |
| `IsDataclass`  | `is_dataclass`              | `-`                                                                           |
| `IsCallable`   | `is_callable`               | `-`                                                                           |
| `IsHashable`   | `is_hashable`               | `-`                                                                           |
| `IsIterable`   | `is_iterable`               | `-`                                                                           |
| `HasAttribute` | `has_attribute`, `has_attr` | `attr_name: str`                                                              |
| `HasLength`    | `has_length`                | `length: int = None`, `*`, `min_length: int = None`, `max_length: int = None` |

➡️ [README_RULE_PREDICATE_INTROSPECTION](https://github.com/simplibs/simplibs-validate/blob/main/docs/rules/README_RULE_PREDICATE_INTROSPECTION.md)

### `predicates/logic/` — identity, membership & custom predicates

| Class      | Shortcut(s)          | Params                                            |
|------------|----------------------|---------------------------------------------------|
| `Is`       | `same_as`, `is_same` | `expected: Any`                                   |
| `IsNot`    | `is_not`             | `forbidden: Any`                                  |
| `IsIn`     | `is_in`              | `options: Container[Any]`, `strict: bool = False` |
| `NotIn`    | `not_in`             | `options: Container[Any]`, `strict: bool = False` |
| `UserRule` | `user_rule`          | `rule: Callable[[Any], bool]`                     |

➡️ [README_RULE_PREDICATE_LOGIC](https://github.com/simplibs/simplibs-validate/blob/main/docs/rules/README_RULE_PREDICATE_LOGIC.md)

> 💡 `Is`/`Not` are Python keywords and can't be used as identifiers directly — their
> shortcuts (`same_as`, `negate`) use a descriptive alternative instead.

### `predicates/numeric/` — numeric type identity

| Class               | Shortcut(s)            | Params                |
|---------------------|------------------------|-----------------------|
| `IsBool`            | `is_bool`              | `-`                   |
| `IsInteger`         | `is_integer`, `is_int` | `-`                   |
| `IsFloat`           | `is_float`             | `-`                   |
| `IsDecimal`         | `is_decimal`           | `-`                   |
| `IsNumber`          | `is_number`            | `-`                   |
| `IsPrimitiveNumber` | `is_primitive_number`  | `-`                   |
| `IsZero`            | `is_zero`              | `-`                   |
| `IsNan`             | `is_nan`               | `-`                   |
| `IsInfinity`        | `is_infinity`          | `-`                   |
| `IsPi`              | `is_pi`                | `decimal_places: int` |

➡️ [README_RULE_PREDICATE_NUMERIC](https://github.com/simplibs/simplibs-validate/blob/main/docs/rules/README_RULE_PREDICATE_NUMERIC.md)

### `predicates/strings/` — string content

| Class           | Shortcut(s)           | Params               |
|-----------------|-----------------------|----------------------|
| `IsString`      | `is_string`, `is_str` | `-`                  |
| `Contains`      | `contains`            | `substring: str`     |
| `IsSubstringOf` | `is_substring_of`     | `target_string: str` |
| `StartsWith`    | `starts_with`         | `prefix: str`        |
| `EndsWith`      | `ends_with`           | `suffix: str`        |
| `Regex`         | `regex`               | `pattern: str`       |
| `IsBlank`       | `is_blank`            | `-`                  |
| `NotBlank`      | `not_blank`           | `-`                  |

➡️ [README_RULE_PREDICATE_STRINGS](https://github.com/simplibs/simplibs-validate/blob/main/docs/rules/README_RULE_PREDICATE_STRINGS.md)

### `typing/` — annotation-driven validation

| Class      | Shortcut(s)             | Params            |
|------------|-------------------------|-------------------|
| `IsAny`    | `is_any`, `always_true` | `-`               |
| `~IsAny`   | `always_false`          | `-`               |
| `IsTyping` | `is_typing`             | `annotation: Any` |

`IsTyping` recursively decomposes an arbitrary type annotation (`list[int]`, `dict[str,
int] | None`, `Literal[...]`, `Callable[...]`, ...) into a composed `Rule` tree —
the mechanism behind `validate_call`/`validate_dataclass`.

➡️ [README_RULE_TYPING](https://github.com/simplibs/simplibs-validate/blob/main/docs/rules/README_RULE_TYPING.md) — the public `IsTyping`/`build_typing_rule` entry points  
➡️ [README_RULE_TYPING_BUILDERS](https://github.com/simplibs/simplibs-validate/blob/main/docs/rules/README_RULE_TYPING_BUILDERS.md) — the internal per-construct decomposition engine

---

## 🧰 Tools

Beyond individual rules, the `tools` package provides the decorators and helpers that
make validation part of a function's or dataclass's own definition:

* **`validate_call`** — validates a function's arguments (and optionally its return
  value) against its own type annotations, on every call. Supports selective
  validation (`check`), extra constraints (`overrides`), and a per-call bypass switch.
* **`validate_dataclass`** — the `@dataclass` counterpart: validates every field
  against its annotation on instance construction, before any field is assigned.
* **`validated_type`** — names a reusable `Annotated[type, rule(s)]` combination once,
  for use across multiple annotations.
* **`override_rules`** — batch-builds the `overrides=` mapping `validate_call`/
  `validate_dataclass` expect, from keyword arguments.
* **`log_this`** — gives any function entry/exit/timing/exception logging, entirely
  independent of validation, without imposing any logging configuration of its own.

➡️ [README_TOOLS](https://github.com/simplibs/simplibs-validate/blob/main/docs/tools/README_TOOLS.md)

---

## ⚠️ Exceptions

Every exception raised by `simplibs-validate` is built on top of
[`simplibs.exception.SimpleException`](https://pypi.org/project/simplibs-exception/) —
structured, readable diagnostic cards instead of a bare traceback.

The library's single common root is `ValidateError`:

```python
class ValidateError(SimpleException):
    """Root exception class for all errors originating from simplibs-validate."""
    skip_locations = ("simplibs/validate",)
```

Two concrete subclasses distinguish *what kind* of mistake occurred:

| Exception         | When it happens                                                                                                                                                                                    |
|-------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `ParamError`      | A **developer error** made while constructing a rule or configuring a decorator — e.g. `HasLength()` with no length source, `validate_call(check=("x",))` where `x` has no annotation or override. |
| `ValidationError` | An **invalid runtime value** — the value being checked simply doesn't satisfy the rule. This is the exception you'll encounter during ordinary, everyday use.                                      |

```python
try:
    validate(-5, greater_than(0))
except ValidateError as e:
    print(e)   # a structured diagnostic card: what, why, how to fix it
```

Catching `ValidateError` catches both categories at once; catching `ValidationError`
or `ParamError` specifically lets you distinguish "bad input data" from "the
validation itself was set up incorrectly." `ValidateError.skip_locations` also filters
the library's own internal frames out of the error's reported location — the message
points to *your* code, not this library's implementation.

---

## 🧪 Testing Utilities

`simplibs-validate` ships with the same testing infrastructure it uses on itself —
useful if you're writing a custom `Rule` subclass or your own `validate_*` wrapper and
want thorough coverage without hand-writing every check.

* **`assert_rule_contract`** — the master facade for testing a `Rule` subclass: one
  call runs the full deterministic battery (`is_valid`/`__call__`, the `validate()`
  return-mode matrix, `build_exception()`'s diagnostic card contract), plus optional
  constructor `ParamError` and `raise_invalid()` consistency checks.
* **`assert_validate_wrapper`** — verifies a `validate_*` convenience function
  correctly wraps its underlying `*_rule` factory and delegates properly to
  `Rule.validate()` — signature alignment, successful/failed delegation, both return
  modes.

➡️ [README_TESTING_ASSERTS_RULE_CONTRACT](https://github.com/simplibs/simplibs-validate/blob/main/docs/testing/README_TESTING_ASSERTS_RULE_CONTRACT.md)
➡️ [README_TESTING_ASSERTS_VALIDATE_WARPER](https://github.com/simplibs/simplibs-validate/blob/main/docs/testing/README_TESTING_ASSERTS_VALIDATE_WARPER.md)  


---

## 🔭 About the library, from the author's point of view

This is the **first version** of `simplibs-validate` — a deliberately focused core
(the `Rule` contract, its composition operators, the annotation-decomposition engine,
and the decorators built on top of it) designed with room to grow, rather than an
attempt to anticipate every possible validation need up front. Real-world use will
show, over time, which additional rules, builders, or tools are worth adding — the
architecture (small, atomized rule classes; a shared `Rule` contract; a single
recursive decomposition entry point for typing) was chosen specifically so that
growth stays easy without ever needing to revisit what's already here.

---

## ☯️ About simplibs

All libraries in the **simplibs** (Simple Libraries) ecosystem share a common
engineering philosophy:

* **Dyslexia-friendly:**
We actively minimize cognitive load. Code is atomized into small, self-contained units,
files are named directly after the logical task they perform, and explanations describe
*why* something is designed, not just *what* it is.
* **Programmer's Zen:**
Nothing should be missing, and nothing should be superfluous. We value clean execution
paths and robust, understandable code architectures over rushed, messy feature sets.
* **Defensive Style:**
We actively anticipate edge cases and failure modes so that only safe operational paths
remain. Our code is built to degrade gracefully rather than crash unexpectedly.
* **Minimalism:**
Find the most direct path to the goal in as few operational steps as possible without
taking shortcuts on safety, readability, or completeness.
* **Code as Craft:**
Code should be pleasant to look at, readable at a glance, and evoke structural harmony.
We treat software engineering as a precision trade.

---

### 🤝 Contributing & Community

This is an **open-source project** built with love and care. We strongly believe in
community collaboration and welcome any feedback, bug reports, or feature ideas!

* **Want to contribute?** Feel free to open an Issue or submit a Pull Request.
* **Want to get in touch?** If you'd like to discuss the project further, collaborate,
  or just say hello, feel free to open a GitHub Issue or start a Discussion.

---

### 📝 License

This library is released under the **MIT License**. Build great things!

---

[▲ Back to Top](#-simplibs-validate)