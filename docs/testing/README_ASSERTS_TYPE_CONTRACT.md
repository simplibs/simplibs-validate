# 🧪 `assert_type_contract`

**Validated Type ↔ Rule Contract & `@validate_call` Integration Master Orchestrator**

`assert_type_contract` is the master entry point for verifying custom or preset type aliases built with `validated_type()` (or `Annotated[type_, *rules]`). It decomposes the target type into its underlying `Rule` tree, hands the entire deterministic contract battery to `simplibs-rules`' `assert_rule_contract`, and optionally verifies that the type works seamlessly when wired directly into `@validate_call`.

## 💡 Table of Contents
> * [⚙️ Architectural Principles](#-architectural-principles)
> * [🧭 Pipeline Execution Flow](#-pipeline-execution-flow)
> * [🔍 Quick Usage Examples](#-quick-usage-examples)
> * [🛠️ Configuration & Parameters](#-configuration--parameters)
> * [🔄 Audit Pipeline (2 Main Phases)](#-audit-pipeline-2-main-phases)
>   * [Phase 1: Rule Contract Battery](#phase-1-rule-contract-battery)
>   * [Phase 2: `@validate_call` Integration](#phase-2-validate_call-integration)
> * [📖 Real-World Example](#-real-world-example)

[⬅️ Back to main README](../../README.md#-testing-utilities)

---

## ⚙️ Architectural Principles

* **Full Type Verification in One Call:** Replaces repetitive, error-prone boilerplate by testing both the decomposed `Rule` behavior and the actual function-annotation execution path in a single assertion.
* **Delegated Core Engine:** Decomposes `type_` using `build_typing_rule(type_)` and hands the entire validation contract (`is_valid`, `validate()`, `build_exception()`) straight to `simplibs-rules`' `assert_rule_contract` without reimplementing rule-level checks.
* **Dual-Path Drift Prevention:** While `build_typing_rule` and `@validate_call` both process type annotations, they execute through separate internal paths. This orchestrator verifies both to ensure no wiring bugs exist between typing decomposition and runtime parameter decoration.

[▲ Back to Top](#-assert_type_contract)

---

## 🧭 Pipeline Execution Flow

1. **Rule Decomposition & Contract Execution** — Decomposes `Annotated[type_, *rules]` into a `Rule` instance and delegates the full deterministic battery (predicate evaluation, return-mode matrix, diagnostic exception cards) to `assert_rule_contract`.
2. **Runtime `@validate_call` Integration** — (When `check_validate_call=True`) Delegates to `assert_type_validate_call_integration` to verify that every valid value is accepted and every invalid value raises a `ValidationError` when used as a parameter annotation.

[▲ Back to top](#-table-of-contents)

---

## 🔍 Quick Usage Examples

```python
from typing import Annotated
from simplibs.rules.predicates import GreaterThan
from simplibs.validate.testing import assert_type_contract
from simplibs.validate.tools import validated_type

# 1. Standard annotated type contract check
PositiveInt = validated_type(int, GreaterThan(0))

assert_type_contract(
    subtests,
    type_=PositiveInt,
    valid_values=[1, 42, 100],
    invalid_values=[-1, 0],
    expected_error_name="GREATER_THAN_ERROR",
)

# 2. Testing rule contract without checking @validate_call integration
assert_type_contract(
    subtests,
    type_=PositiveInt,
    valid_values=[1, 10],
    invalid_values=[-5],
    check_validate_call=False,
    verbose=False,
)

```

[▲ Back to Top](#-assert_type_contract)

---

## 🛠️ Configuration & Parameters

### Mandatory Parameters

* **`subtests`** (`Any`): The native pytest subtests fixture manager instance.
* **`type_`** (`Any`): The target type under test — an `Annotated[type_, *rules]` construct or named alias.
* **`valid_values`** (`list[Any]`): List of sample inputs expected to satisfy the type.
* **`invalid_values`** (`list[Any]`): List of sample inputs expected to fail validation and produce a `ValidationError`.

### Optional Parameters

* **`expected_error_name`** (`str | None`): Default `None`. Expected `error_name` string on generated exceptions.
* **`expected_exception_type`** (`type[Exception] | None`): Default `None`. Expected underlying exception class wrapped inside the `ValidationError`.
* **`sample_label`** (`str`): Default `"target_var"`. Label used during exception diagnostic probing.
* **`sample_context`** (`str`): Default `"test_execution_context"`. Context string used during exception diagnostic probing.
* **`check_value`** (`bool`): Default `True`. Asserts that `exc.value` matches the input value strictly.
* **`check_validate_call`** (`bool`): Default `True`. Triggers the `@validate_call` integration test phase.
* **`verbose`** (`bool`): Default `True`. Enables isolated pytest subtest registration.
* **`intro`** (`str`): Default `""`. Prefix prepended to pytest subtest identity strings.
* **`deep_check`** (`bool`): Default `True`. Triggers exhaustive field-level diagnostic verification.

```python
# Function signature:
def assert_type_contract(
    subtests: Any,
    type_: Any,
    valid_values: list[Any],
    invalid_values: list[Any],
    *,
    expected_error_name: str | None = None,
    expected_exception_type: type[Exception] | None = None,
    sample_label: str = "target_var",
    sample_context: str = "test_execution_context",
    check_value: bool = True,
    check_validate_call: bool = True,
    verbose: bool = True,
    intro: str = "",
    deep_check: bool = True,
) -> None:

```

[▲ Back to Top](#-assert_type_contract)

---

## 🔄 Audit Pipeline (2 Main Phases)

### Phase 1: Rule Contract Battery

Decomposes the input `type_` using `build_typing_rule(type_)` and forwards the resulting `Rule` object directly to `assert_rule_contract` from `simplibs-rules`.

```python
# Executed under the hood:
rule = build_typing_rule(type_)

assert_rule_contract(
    subtests,
    rule,
    valid_values,
    invalid_values,
    expected_error_name=expected_error_name,
    expected_exception_type=expected_exception_type,
    sample_label=sample_label,
    sample_context=sample_context,
    check_value=check_value,
    verbose=verbose,
    intro=intro,
    deep_check=deep_check,
)

```

### Phase 2: `@validate_call` Integration

When `check_validate_call=True`, invokes `assert_type_validate_call_integration` to verify that the type behaves as expected when decorating actual function parameters.

```python
# Executed under the hood:
if check_validate_call:
    assert_type_validate_call_integration(
        subtests,
        type_,
        valid_values,
        invalid_values,
        verbose=verbose,
        intro=intro,
    )

```

[▲ Back to Top](#-assert_type_contract)

---

## 📖 Real-World Example

```python
"""Tests for a custom PositiveInt type contract."""

import pytest
from simplibs.rules.predicates import GreaterThan
from simplibs.validate.testing import assert_type_contract
from simplibs.validate.tools import validated_type

PositiveInt = validated_type(int, GreaterThan(0))

def test_positive_int_contract(subtests):
    """Verify that PositiveInt satisfies both Rule and @validate_call contracts."""
    assert_type_contract(
        subtests,
        type_=PositiveInt,
        valid_values=[1, 10, 100],
        invalid_values=[-5, 0],
        expected_error_name="GREATER_THAN_ERROR",
        verbose=False,
    )

```

[▲ Back to Top](#-assert_type_contract)

---

[⬅️ Back to main README](../../README.md#-testing-utilities)

