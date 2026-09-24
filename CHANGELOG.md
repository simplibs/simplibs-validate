# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [0.2.1] - 2026-09-24

### 📋 Improved

#### Testing Utils (`simplibs.validate.testing`)

* **Enhanced Contract Assertions for `Sequence` Inputs in `assert_type_contract`**:
  * Updated type annotations and parameter passing for `expected_error_name` and `expected_exception_type` to accept index-matched `Sequence` instances (or `Sequence[... | None]`).
  * Aligned `assert_type_contract` with `simplibs-rules` (v0.2.2) to support multi-error types where different invalid inputs trigger distinct underlying diagnostic error names or exception types.

---

## [0.2.0] - 2026-09-23

### ⚠️ Breaking Changes

* **Rule engine extracted into `simplibs-rules`**: the `Rule` base class, every
  container rule (`AllOf`, `AnyOf`, `NoneOf`, `Not`, `ForEach`, `Compose`), every
  predicate package (`arithmetic`, `checkers`, `collections`, `comparisons`,
  `introspection`, `logic`, `numeric`, `strings`), the snake-case shortcuts and
  `rule_class`/`rules` namespaces, and the whole annotation-decomposition engine
  (`IsTyping`, `build_typing_rule`, `IsAny`, `is_supported_annotation`,
  `get_supported_origins`) no longer live in `simplibs-validate` — they've moved to the
  new standalone [`simplibs-rules`](https://pypi.org/project/simplibs-rules/) library,
  now a core dependency of this package. Import them from `simplibs.rules` instead of
  `simplibs.validate`.
* **Testing utilities narrowed accordingly**: `assert_rule_contract` and its atomic
  assertions (`assert_rule_is_valid`, `assert_rule_validate`,
  `assert_rule_build_exception`, `assert_rule_raise_invalid`, `assert_rule_param_error`)
  moved to `simplibs-rules` — they test the `Rule` contract itself, not anything
  specific to this library.

### ✨ Added

* **Type Testing Utilities (`testing/`)**:
  * `assert_type_contract`: master orchestrator utility that verifies an annotated type's
    contract, ensuring both its underlying rule decomposition and its integration with
    `@validate_call` work properly against valid and invalid inputs.
  * `assert_type_validate_call_integration`: specialized integration assertion testing
    a type's execution when passed directly through `@validate_call`.

### 🔄 Changed

* **Why the split**: the atomic rule engine and its annotation-decomposition machinery
  are genuinely independent of the validation entry point, wrappers, and decorators
  this library builds on top of them — other tools may want the rules without the
  `validate_call`/`validate_dataclass` layer, or vice versa. Separating them into their
  own library keeps each dependency honest and each package's surface focused on one
  job, rather than one growing package doing all of it.
* `simplibs-validate`'s own surface is now focused on: the `validate()` entry point;
  `raise_invalid()`; the specialized validators (`*_rule` composers and their
  `validate_*` wrappers); tools (`validate_call`/`validate_dataclass`/`override_rules`/
  `validated_type`/`log_this`); and testing utilities (`assert_validate_wrapper`,
  `assert_type_contract`, `assert_type_validate_call_integration`).
* `simplibs-validate` now depends on `simplibs-rules` for the `Rule` contract,
  predicates, and typing-decomposition engine that `validate_call`/`validate_dataclass`
  still rely on internally.

### 📋 Improved

* **Documentation**: main README rewritten to reflect the split, with a two-layer
  architecture diagram (`simplibs-rules` → `validate()` → validators/tools) replacing
  the previous three-layer, single-library one, and cross-links to `simplibs-rules`
  throughout.

---

## [0.1.0] - 2026-09-08

### ✨ Added

#### Core Functions

* `validate(value, rule, *, value_name=None, context=None, return_bool=False, return_value=False)` — universal validation entry point, accepting either a `Rule` instance or a plain callable predicate
* `raise_invalid(value, rule, *, value_name=None, context=None)` — unconditional diagnostic-exception dispatcher for code paths that have already determined a value is invalid, without re-evaluating the rule

#### `Rule` — Base Class

* Abstract `is_valid(value)` / `build_exception(value, value_name, context)` contract every rule implements
* `validate(...)` — the full return-mode interface (raise / `True`/`False` / value)
* `__call__` — predicate shorthand (`rule(value)`)
* Operator-based composition: `|` (`AnyOf`), `&` (`AllOf`), `~` (`Not`), including reflected (`__ror__`/`__rand__`) support for plain callables on the left-hand side
* `annotated(type_)` — bridges any `Rule` directly into `typing.Annotated[type_, self]`

#### Container Rules (`rules/containers/`)

* `AllOf`, `AnyOf`, `NoneOf` — variadic composition (all/any/none of the given rules), with automatic flattening of same-type nested instances from operator chaining
* `Not` — single-rule negation
* `ForEach` — per-item validation over an iterable, with per-index failure diagnostics
* `Compose` — transform-then-validate, for normalize-before-check patterns

#### Predicate Rules (`rules/predicates/`)

* **Arithmetic**: `CloseTo`, `DivisibleBy`, `HasRemainder`
* **Checkers**: `IsNone`, `IsTrue`, `IsFalse` (identity-based), `IsEmpty`, `NotEmpty`
* **Collections**: `AllUnique`, `HasItem`, `HasKey`, `HasKeys`, `IsContainer`, `IsSubsetOf`, `IsSupersetOf`
* **Comparisons**: `Equals`, `NotEquals`, `GreaterThan`, `GreaterOrEqual`, `LessThan`, `LessOrEqual`, `InRange` (configurable bound inclusivity)
* **Introspection**: `IsInstance`, `IsType`, `IsSubclass`, `IsDataclass`, `IsCallable`, `IsHashable`, `IsIterable`, `HasAttribute`, `HasLength`
* **Logic**: `Is`, `IsNot` (identity), `IsIn`, `NotIn` (membership, with optional `strict` type-exact matching), `UserRule` (wraps an arbitrary callable predicate, with constructor-time arity validation)
* **Numeric**: `IsBool`, `IsInteger`, `IsFloat`, `IsDecimal`, `IsNumber`, `IsPrimitiveNumber`, `IsZero`, `IsNan`, `IsInfinity`, `IsPi` — booleans consistently excluded from every "real number" check
* **Strings**: `IsString`, `Contains`, `IsSubstringOf`, `StartsWith`, `EndsWith`, `Regex`, `IsBlank`, `NotBlank`

#### Snake-Case Shortcuts & Namespaces

* A pre-instantiated or class-level snake_case shortcut for every built-in rule (e.g. `is_integer`, `greater_than`, `regex`), fully interchangeable with and composable alongside the class form
* `rule_class` — `SimpleNamespace` exposing every concrete `Rule` subclass under its original class name, for `isinstance` checks, subclassing, and programmatic construction
* `rules` — `SimpleNamespace` exposing every public shortcut, functionally equivalent to direct imports

#### Annotation-Driven Validation (`rules/typing/`)

* `IsTyping(annotation)` — recursively decomposes an arbitrary type annotation into a composed `Rule` tree, built once at construction
* `build_typing_rule(annotation)` — the recursive dispatcher underlying `IsTyping`, also used directly by `validate_call`/`validate_dataclass`
* `IsAny` — the structural counterpart to `typing.Any` within the decomposition tree
* A dispatch table (`ORIGIN_TABLE`) and a family of per-process builders covering: element collections (`list`/`set`/`frozenset`/`Iterable`/`Sequence`/`Collection`), key-value mappings (`dict`/`Mapping`/`MutableMapping`), homogeneous and fixed-length tuples, unions (`Union`/`X | Y`, including `Optional` for free), `Literal` (with strict type-exact matching), `Type`/`type` (including `Union` and `Any` bases), `Callable`, and `Annotated` metadata unpacking
* Support for both modern (`collections.abc`) and legacy (`typing.List`, `typing.Dict`, ...) annotation spellings
* `NewType` unwrapping and direct use of a `Rule` instance as an annotation, both handled transparently by `build_typing_rule`
* `is_supported_annotation(annotation)` / `get_supported_origins()` — read-only introspection helpers for what the decomposition engine currently supports

#### Specialized Validators (`validators/`)

* `*_rule(...)` composers — `boolean_rule`, `container_rule`, `float_rule`, `integer_rule`, `mapping_rule`, `number_rule`, `string_rule`, `type_rule` — each building a single composed `Rule` from a flat set of optional keyword constraints
* `validate_*(value, ...)` — matching thin wrappers (`validate_bool`, `validate_container`, `validate_float`, `validate_int`, `validate_mapping`, `validate_number`, `validate_string`, `validate_type`) composing their `*_rule` and delegating straight to `Rule.validate(...)`

#### Tools (`tools/`)

* `validate_call` — decorator validating a function's arguments (and, opt-in, its return value) against its own type annotations on every call; supports selective validation (`check`), extra per-parameter constraints (`overrides`), and a reserved per-call `validate: bool` bypass parameter; fully signature-preserving via `@overload` + `ParamSpec`; native `async def` support
* `validate_dataclass` — the `@dataclass` counterpart, validating every field against its own annotation before any field is assigned (safe for frozen dataclasses), reusing `validate_call`'s own per-parameter rule compiler
* `validated_type(type_, *rules)` — names a reusable `Annotated[type_, *rules]` combination for use across multiple annotations
* `override_rules(**rules)` — batch-builds a parameter-name → `Rule` mapping for `overrides=`, from keyword arguments
* `log_this` — decorator giving any function (sync or `async`) entry/exit/timing/exception logging through the caller's own `logging` configuration, with argument masking (`exclude`), optional result/exception suppression, and zero imposed logging setup

#### Exceptions

* `ValidateError` — single root exception for the library, built on `simplibs.exception.SimpleException`, producing structured diagnostic cards (`expected`/`problem`/`how_to_fix`) instead of bare tracebacks
* `ParamError` — developer-error subclass, raised for invalid rule construction or decorator configuration
* `ValidationError` — runtime-error subclass, raised when an actual value fails a rule
* Every rule's diagnostic card is independently constructible (`build_exception`) and raisable (`validate`/`raise_invalid`)

#### Testing Utilities (`testing/`)

* `assert_rule_contract` — master facade running the full deterministic `Rule` contract battery: `is_valid`/`__call__`, the `validate()` return-mode matrix, `build_exception()`'s diagnostic-card contract, plus optional constructor `ParamError` and `raise_invalid()` consistency checks
* `assert_rule_is_valid`, `assert_rule_validate`, `assert_rule_build_exception`, `assert_rule_raise_invalid`, `assert_rule_param_error` — the atomic assertions `assert_rule_contract` composes, each independently usable
* `assert_validate_wrapper` — verifies a `validate_*` wrapper correctly mirrors and delegates to its underlying `*_rule` factory

#### Documentation

* Full reference documentation for the `Rule` base class, every rule package, the typing-decomposition engine and its builders, every specialized validator, every tool, and the testing utilities
* Complete rule quick-reference tables (class / shortcut / call signature) in the main README

#### Dependencies

* `simplibs-exception` — structured exception framework underlying `ValidateError`
* `simplibs-sentinels` — sentinel values (`UNSET`) for distinguishing unset arguments from `None` (e.g. `mapping_rule`'s `has_key`)

---

## Legend

* 🔄 **Changed** — modifications to existing functionality
* ✨ **Added** — new features and components
* 🐛 **Fixed** — bug fixes
* 📋 **Improved** — enhancements to existing features
* ⚠️ **Deprecated** — deprecated functionality (not used yet in this project)
* 🗑️ **Removed** — removed functionality (not used yet in this project)