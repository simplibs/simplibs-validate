# ⚖️ `simplibs-validate`

[![PyPI](https://img.shields.io/pypi/v/simplibs-validate)](https://pypi.org/project/simplibs-validate/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![Licence](https://img.shields.io/badge/licence-MIT-green)](https://github.com/simplibs/simplibs-validate/blob/main/LICENSE)

**The validation layer on top of [`simplibs-rules`](https://pypi.org/project/simplibs-rules/) — entry points, ready-made validators, and self-validating decorators.**

`simplibs-rules` defines the atomic `Rule` objects and lets you compose them with
`|`/`&`/`~`. `simplibs-validate` is what turns a rule (or a whole function signature)
into an actual validation *action*: a single `validate()` call, a batteries-included
`validate_*` wrapper for common types, or a decorator that validates a function or
dataclass automatically from its own type hints.

```python
from simplibs.validate import validate
from simplibs.rules import is_integer, greater_than

validate(5, is_integer & greater_than(0))          # -> True
validate(-5, is_integer & greater_than(0))          # -> raises ValidationError
```

---

## 🧭 The Core Philosophy

`simplibs-validate` doesn't define new predicates of its own — that's
[`simplibs-rules`](https://pypi.org/project/simplibs-rules/)'s job. What it adds is the
layer people actually reach for day to day: a universal `validate()` entry point,
ready-made `validate_*` functions for common types so you rarely need to hand-compose a
rule tree, and decorators that make an entire function or dataclass self-validating from
nothing more than its own type annotations:

```python
from simplibs.validate import validate_call
from simplibs.types import validated_type
from simplibs.rules import greater_than

PositiveInt = validated_type(int, greater_than(0))

@validate_call
def register(age: PositiveInt, *, validate: bool = True) -> None:
    ...

register(25)                       # validated normally
register(-5)                       # raises ValidationError
register(-5, validate=False)       # explicitly skipped — e.g. already validated upstream
```

That combination — annotation-driven rules from `simplibs-rules`, named reusable types
from `simplibs-types`, and a decorator that enforces them automatically with a per-call
opt-out for code paths that already trust their data — is what lets you build fully
self-validating functions and dataclasses from nothing more than their own signatures.

---

## 📦 Installation

```bash
pip install simplibs-validate
```

`simplibs-rules` is installed automatically as a dependency — its rules and operators
(`is_integer`, `greater_than`, `IsTyping`, ...) are what you pass into everything below.

---

## 🚀 Quick Start in 60 Seconds

### Level 1: One-off validation

```python
from simplibs.validate import validate
from simplibs.rules import is_integer, greater_than

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
┌──────────────────────────┐
│      simplibs-rules      │ ◄── Rule subclasses + snake_case shortcuts
└────────────┬─────────────┘
             ▼
┌──────────────────────────┐
│        validators        │ ◄── validate, raise_invalid, validate_string, validate_int, ... 
└────────────┬─────────────┘
             ▼
┌──────────────────────────┐
│    decorators & tools    │ ◄── validate_call, validate_dataclass, log_this, ...
└──────────────────────────┘
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

## 🧰 Tools

Beyond individual rules, the `decorators` and `tools` packages provide the
convenience layers that make validation part of a function's or dataclass's
definition:

### 🎀 Decorators

The `decorators` package provides decorators that add validation or structured
logging directly to functions and dataclasses:

* **`validate_call`** — validates a function's arguments (and optionally its return
  value) against its own type annotations, on every call. Supports selective
  validation (`check`), extra constraints (`overrides`), and a per-call bypass switch.
* **`validate_dataclass`** — the `@dataclass` counterpart: validates every field
  against its annotation on instance construction, before any field is assigned.
* **`log_this`** — gives any function entry/exit/timing/exception logging, entirely
  independent of validation, without imposing any logging configuration of its own.

➡️ [README_DECORATORS](https://github.com/simplibs/simplibs-validate/blob/main/docs/decorators/README_DECORATORS.md)

### 🛠️ Tools

The `tools` package provides small helpers used to build reusable validation
annotations and the rule mappings consumed by the decorators:

* **`validated_type`** — names a reusable `Annotated[type, rule(s)]` combination once,
  for use across multiple annotations.
* **`override_rules`** — batch-builds the `overrides=` mapping `validate_call`/
  `validate_dataclass` expect, from keyword arguments.

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

`simplibs-validate` ships with testing infrastructure for the layer it owns — the
wrappers, decorators, and validated types, not the underlying atomic rules (see `simplibs-rules`'
`assert_rule_contract` for that):

* **`assert_validate_wrapper`** — verifies a `validate_*` convenience function
  correctly wraps its underlying `*_rule` factory and delegates properly to
  `Rule.validate()` — signature alignment, successful/failed delegation, both return
  modes.
* **`assert_type_contract`** — master orchestrator that verifies a `validated_type()`-built
  construct against the full `Rule` contract battery (by decomposing it via `build_typing_rule`)
  and optionally tests its execution under `@validate_call`.
* **`assert_type_validate_call_integration`** — specialized integration probe verifying that
  a custom type annotation is correctly intercepted and enforced when used on parameters of
  a `@validate_call`-decorated function.

➡️ [README_TESTING_ASSERTS_VALIDATE_WRAPPER](https://github.com/simplibs/simplibs-validate/blob/main/docs/testing/README_TESTING_ASSERTS_VALIDATE_WRAPPER.md)  
➡️ [README_ASSERT_TYPE_CONTRACT](https://github.com/simplibs/simplibs-validate/blob/main/docs/testing/README_ASSERT_TYPE_CONTRACT.md)  
➡️ [README_ASSERT_TYPE_VALIDATE_CALL_INTEGRATION](https://github.com/simplibs/simplibs-validate/blob/main/docs/testing/README_ASSERT_TYPE_VALIDATE_CALL_INTEGRATION.md)


---

## 🔭 About the library, from the author's point of view

`simplibs-validate` used to bundle the rule engine itself; that engine has since moved
to its own library, [`simplibs-rules`](https://pypi.org/project/simplibs-rules/), so
that the atomic predicates can be depended on independently of the higher-level
validation entry points and decorators defined here. What remains here is deliberately
focused: `validate()`, the `validate_*` convenience layer, and the
`validate_call`/`validate_dataclass` decorators — with room to grow as real-world use
shows which additional wrappers or tools are worth adding.

---

## 🔗 Related libraries

* **[`simplibs-rules`](https://pypi.org/project/simplibs-rules/)** — the `Rule` base
  class, operator composition, and every built-in predicate (`is_integer`,
  `greater_than`, `IsTyping`, ...) used throughout this library.
* **[`simplibs-types`](https://pypi.org/project/simplibs-types/)** *(in progress)* — reusable, named validated types
  (`validated_type` and friends) built on `simplibs-rules`, for sharing a single
  constraint definition across many `validate_call`/`validate_dataclass` annotations.

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